from __future__ import annotations

import asyncio
import contextlib
import re
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.runtime.execution_manager import ExecutionManager
from backend.app.schemas.process_state import ProcessStateSchema
from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.card_transition_service import advance_card_to_contract
from backend.app.services.chat_service import append_normalized_log_entry
from backend.app.services.execution_log_service import write_execution_log
from backend.app.services.execution_process_service import (
    create_execution_process,
    list_execution_processes,
    update_execution_process_status,
)
from backend.app.services.issue_projection_service import build_issue_rows
from backend.app.services.issues_csv_service import generate_issues_csv, validate_issues_csv
from backend.app.services.plan_precheck_service import run_plan_precheck
from backend.app.services.plan_prompt_builder import build_plan_prompt
from backend.app.services.process_state_service import update_process_state
from backend.app.services.session_service import create_session_record, mark_session_status, session_to_payload
from common.core.database import get_session_factory
from common.core.exceptions import ValidationError
from common.core.logger import logger
from common.core.request_context import apply_request_context, clear_request_context, copy_request_context, set_request_context

PLAN_RUNTIME_MANAGER = ExecutionManager()
PLAN_BACKGROUND_TASKS: dict[str, asyncio.Task[None]] = {}
PLAN_RUNTIME_KEYS: dict[str, str] = {}


# Plan 进程服务负责驱动生成执行合同、产出 Issues CSV，并维护 plan 阶段状态流转。
def _extract_scalar_field(block: str, field_name: str, default: str = "") -> str:
    match = re.search(rf"- `{re.escape(field_name)}`:\s*(.+)", block)
    if not match:
        return default
    return match.group(1).strip()


def _extract_list_field(block: str, field_name: str) -> list[str]:
    match = re.search(rf"- `{re.escape(field_name)}`:\s*\n((?:\s{{2,}}- .*\n?)*)", block)
    if not match:
        return []
    items: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def parse_issue_contracts(plan_content: str) -> list[dict[str, Any]]:
    if "## View 2: Issue Contract" not in plan_content:
        raise ValidationError("Plan 缺少 View 2: Issue Contract")
    view = plan_content.split("## View 2: Issue Contract", 1)[1]
    sections = re.split(r"^###\s+", view, flags=re.MULTILINE)
    issues: list[dict[str, Any]] = []
    for section in sections:
        stripped = section.strip()
        if not stripped or stripped.startswith("Issue 列表概览"):
            continue
        issue_id = _extract_scalar_field(stripped, "id")
        if not issue_id:
            continue
        issues.append(
            {
                "id": issue_id,
                "priority": _extract_scalar_field(stripped, "priority", "P1"),
                "title": _extract_scalar_field(stripped, "title", issue_id),
                "summary": _extract_scalar_field(stripped, "summary"),
                "design_refs": _extract_list_field(stripped, "design_refs"),
                "code_refs": _extract_list_field(stripped, "code_refs"),
                "acceptance_criteria": _extract_list_field(stripped, "acceptance_criteria"),
                "test_cases": _extract_list_field(stripped, "test_cases"),
                "constraints": _extract_list_field(stripped, "constraints"),
                "depends_on": _extract_scalar_field(stripped, "depends_on", "无"),
                "notes": _extract_scalar_field(stripped, "notes", ""),
            }
        )
    if not issues:
        raise ValidationError("Plan Issue Contract 不能为空")
    logger.info("已解析 Issue Contract count={}", len(issues))
    return issues


def _cleanup_output_paths(output_paths: dict[str, str]) -> None:
    for key in ("plan_path", "issues_path"):
        path = Path(output_paths[key])
        with contextlib.suppress(FileNotFoundError):
            path.unlink()
            logger.warning("已清理输出文件 key={} path={}", key, path)


async def _latest_execution_process_payload(session: AsyncSession, session_id: str | None) -> dict[str, Any] | None:
    if not session_id:
        return None
    processes = await list_execution_processes(session, session_id=session_id)
    if not processes:
        return None
    return processes[0]


async def _persist_execution_event(
    session: AsyncSession,
    session_id: str,
    execution_process_id: str,
    event: dict[str, Any],
) -> None:
    set_request_context(session_id=session_id, execution_process_id=execution_process_id, channel="process")
    await write_execution_log(
        session,
        execution_process_id,
        stream=event.get("stream", "stdout"),
        event_type=event["event_type"],
        raw_text=event.get("raw_text"),
        payload=event.get("payload"),
    )
    await append_normalized_log_entry(
        session,
        session_id,
        event,
        execution_process_id=execution_process_id,
    )
    await session.commit()
    logger.debug(
        "已持久化 plan 执行事件 session_id={} execution_process_id={} event_type={}",
        session_id,
        execution_process_id,
        event["event_type"],
    )


async def _finalize_plan_success(
    session: AsyncSession,
    card_id: str,
    session_id: str,
    execution_process_id: str,
    precheck: dict[str, Any],
    exit_code: int | None,
) -> dict[str, Any]:
    logger.info(
        "开始收口 plan 成功结果 card_id={} session_id={} execution_process_id={} exit_code={}",
        card_id,
        session_id,
        execution_process_id,
        exit_code,
    )
    output_paths = precheck["output_paths"]
    plan_path = Path(output_paths["plan_path"])
    issues_path = Path(output_paths["issues_path"])
    if not plan_path.exists():
        raise ValidationError(f"Plan file not found: {plan_path}")

    issue_contracts = parse_issue_contracts(plan_path.read_text(encoding="utf-8"))
    if issues_path.exists():
        issues_path.unlink()
    issue_rows = build_issue_rows(issue_contracts)
    generate_issues_csv(issue_rows, issues_path)
    validate_issues_csv(issues_path)

    card = await get_card_or_raise(session, card_id)
    card.plan_path = str(plan_path)
    card.issues_path = str(issues_path)
    await session.flush()

    await advance_card_to_contract(session, card_id)
    process_payload = await update_execution_process_status(
        session,
        execution_process_id,
        "finished",
        exit_code=exit_code,
        last_error=None,
        dropped=False,
    )
    await mark_session_status(session, session_id, "completed")
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_plan",
            active_process_status="finished",
            active_process_session_id=session_id,
        ),
    )
    updated_card = await get_card_or_raise(session, card_id)
    return {
        "card_id": updated_card.id,
        "current_stage": updated_card.current_stage,
        "plan_path": updated_card.plan_path,
        "issues_path": updated_card.issues_path,
        "execution_process": process_payload,
    }


async def _finalize_plan_failure(
    session: AsyncSession,
    card_id: str,
    session_id: str,
    execution_process_id: str | None,
    reason: str,
    status: str = "failed",
    exit_code: int | None = None,
) -> dict[str, Any]:
    logger.warning(
        "开始收口 plan 失败结果 card_id={} session_id={} execution_process_id={} status={} reason={}",
        card_id,
        session_id,
        execution_process_id,
        status,
        reason,
    )
    card = await get_card_or_raise(session, card_id)
    normalized_status = status if status in {"failed", "stopped", "aborted"} else "failed"
    if execution_process_id is not None:
        await update_execution_process_status(
            session,
            execution_process_id,
            normalized_status,
            exit_code=exit_code,
            last_error=reason,
            dropped=True,
        )
    await mark_session_status(session, session_id, "failed")
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_plan",
            active_process_status="failed",
            active_process_session_id=session_id,
        ),
    )
    refreshed = await get_card_or_raise(session, card_id)
    return {
        "card_id": refreshed.id,
        "current_stage": refreshed.current_stage,
        "active_process_type": refreshed.active_process_type,
        "active_process_status": refreshed.active_process_status,
        "reason": reason,
    }


async def _run_plan_runtime(
    card_id: str,
    session_id: str,
    execution_process_id: str,
    runtime_execution_id: str,
    precheck: dict[str, Any],
    request_context: dict[str, Any],
) -> None:
    factory = get_session_factory()
    apply_request_context(request_context)
    set_request_context(
        card_id=card_id,
        session_id=session_id,
        execution_process_id=execution_process_id,
        channel="process",
        transport="runtime",
    )
    logger.info(
        "plan runtime 已启动 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
        card_id,
        session_id,
        execution_process_id,
        runtime_execution_id,
    )
    try:
        chunks = await PLAN_RUNTIME_MANAGER.collect(runtime_execution_id)
        async with factory() as session:
            for chunk in chunks:
                await _persist_execution_event(session, session_id, execution_process_id, chunk)

        result = await PLAN_RUNTIME_MANAGER.wait(runtime_execution_id)
        logger.info(
            "plan runtime 等待结束 runtime_execution_id={} status={} exit_code={}",
            runtime_execution_id,
            result.get("status"),
            result.get("exit_code"),
        )
        async with factory() as session:
            if result["status"] == "finished":
                await _finalize_plan_success(
                    session,
                    card_id,
                    session_id,
                    execution_process_id,
                    precheck,
                    result.get("exit_code"),
                )
            else:
                _cleanup_output_paths(precheck["output_paths"])
                await _persist_execution_event(
                    session,
                    session_id,
                    execution_process_id,
                    {
                        "event_type": "error",
                        "stream": "stderr",
                        "raw_text": f"plan process {result['status']}",
                        "payload": {"status": result["status"], "exit_code": result.get("exit_code")},
                    },
                )
                await _finalize_plan_failure(
                    session,
                    card_id,
                    session_id,
                    execution_process_id,
                    reason=f"plan process {result['status']}",
                    status=result["status"],
                    exit_code=result.get("exit_code"),
                )
    except Exception as exc:
        logger.exception(
            "plan runtime 执行失败 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
            card_id,
            session_id,
            execution_process_id,
            runtime_execution_id,
        )
        async with factory() as session:
            _cleanup_output_paths(precheck["output_paths"])
            await _persist_execution_event(
                session,
                session_id,
                execution_process_id,
                {
                    "event_type": "error",
                    "stream": "stderr",
                    "raw_text": str(exc),
                    "payload": {"error": str(exc)},
                },
            )
            await _finalize_plan_failure(
                session,
                card_id,
                session_id,
                execution_process_id,
                reason=str(exc),
                status="failed",
            )
    finally:
        PLAN_RUNTIME_KEYS.pop(execution_process_id, None)
        PLAN_BACKGROUND_TASKS.pop(execution_process_id, None)
        logger.info(
            "plan runtime 已清理 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
            card_id,
            session_id,
            execution_process_id,
            runtime_execution_id,
        )
        clear_request_context()


async def start_plan_process(session: AsyncSession, card_id: str) -> dict[str, Any]:
    set_request_context(card_id=card_id, channel="process")
    logger.info("开始执行 plan 流程 card_id={}", card_id)
    precheck = await run_plan_precheck(session, card_id)
    session_record = await create_session_record(session, card_id, stage_key="plan", session_type="skill_plan")
    prompt = build_plan_prompt(precheck)
    runtime_execution_id = f"plan-{session_record.id}"
    runtime = await PLAN_RUNTIME_MANAGER.start(runtime_execution_id, prompt)
    execution_process = await create_execution_process(
        session,
        session_record.id,
        run_reason="skill_plan",
        executor_action={
            "command": runtime["command"],
            "prompt": prompt,
            "output_paths": precheck["output_paths"],
            "requirements_path": precheck["requirements_path"],
        },
        pid=runtime.get("pid"),
    )
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_plan",
            active_process_status="running",
            active_process_session_id=session_record.id,
        ),
    )
    request_context = copy_request_context()
    request_context.update(
        {
            "card_id": card_id,
            "session_id": session_record.id,
            "execution_process_id": execution_process["id"],
            "channel": "process",
            "transport": "runtime",
        }
    )
    PLAN_RUNTIME_KEYS[execution_process["id"]] = runtime_execution_id
    PLAN_BACKGROUND_TASKS[execution_process["id"]] = asyncio.create_task(
        _run_plan_runtime(
            card_id,
            session_record.id,
            execution_process["id"],
            runtime_execution_id,
            precheck,
            request_context,
        )
    )
    logger.info(
        "已调度 plan runtime 后台任务 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
        card_id,
        session_record.id,
        execution_process["id"],
        runtime_execution_id,
    )
    return {
        "precheck": precheck,
        "session": session_to_payload(session_record),
        "execution_process": execution_process,
        "prompt": prompt,
    }


async def finish_plan_process(session: AsyncSession, card_id: str) -> dict[str, Any]:
    logger.info("开始手动完成 plan 流程 card_id={}", card_id)
    card = await get_card_or_raise(session, card_id)
    if card.active_process_type != "skill_plan":
        raise ValidationError("当前卡片没有 plan process")
    session_id = card.active_process_session_id
    execution_process = await _latest_execution_process_payload(session, session_id)
    if not session_id or execution_process is None:
        raise ValidationError("当前卡片缺少 plan process 上下文")
    executor_action = execution_process.get("executor_action") or {}
    precheck = {
        "output_paths": executor_action.get("output_paths") or {},
        "requirements_path": executor_action.get("requirements_path"),
    }
    if not precheck["output_paths"]:
        raise ValidationError("当前 plan process 缺少产物路径信息")
    return await _finalize_plan_success(
        session,
        card_id,
        session_id,
        execution_process["id"],
        precheck,
        exit_code=execution_process.get("exit_code"),
    )


async def fail_plan_process(session: AsyncSession, card_id: str, reason: str) -> dict[str, Any]:
    if not reason.strip():
        raise ValidationError("Failure reason cannot be empty")
    logger.warning("开始标记 plan 流程失败 card_id={} reason={}", card_id, reason)
    card = await get_card_or_raise(session, card_id)
    if card.current_stage != "plan":
        raise ValidationError("plan 失败回滚只能发生在 plan 阶段")
    if card.active_process_type != "skill_plan":
        raise ValidationError("当前卡片没有运行中的 plan process")
    if card.active_process_status not in {"running", "failed"}:
        raise ValidationError("只有运行中或失败中的 plan process 才能回滚")

    session_id = card.active_process_session_id
    execution_process = await _latest_execution_process_payload(session, session_id)
    if not session_id:
        raise ValidationError("当前卡片缺少 plan session")

    if execution_process is not None:
        runtime_execution_id = PLAN_RUNTIME_KEYS.get(execution_process["id"])
        if runtime_execution_id is not None:
            await PLAN_RUNTIME_MANAGER.fail(runtime_execution_id, reason)
        task = PLAN_BACKGROUND_TASKS.get(execution_process["id"])
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        executor_action = execution_process.get("executor_action") or {}
        output_paths = executor_action.get("output_paths") or {}
        if output_paths:
            _cleanup_output_paths(output_paths)
        await _persist_execution_event(
            session,
            session_id,
            execution_process["id"],
            {
                "event_type": "error",
                "stream": "stderr",
                "raw_text": reason,
                "payload": {"reason": reason},
            },
        )

    return await _finalize_plan_failure(
        session,
        card_id,
        session_id,
        execution_process["id"] if execution_process is not None else None,
        reason=reason,
        status="failed",
    )
