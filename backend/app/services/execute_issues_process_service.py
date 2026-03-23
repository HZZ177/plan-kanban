from __future__ import annotations

import asyncio
import contextlib
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.runtime.execution_manager import ExecutionManager
from backend.app.schemas.process_state import ProcessStateSchema
from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.card_transition_service import advance_card_to_acceptance, advance_card_to_developing
from backend.app.services.chat_service import append_normalized_log_entry
from backend.app.services.execute_issues_prompt_builder import build_execute_issues_prompt
from backend.app.services.execute_precheck_service import run_execute_precheck
from backend.app.services.execution_log_service import write_execution_log
from backend.app.services.execution_process_service import (
    create_execution_process,
    list_execution_processes,
    update_execution_process_status,
)
from backend.app.services.issue_runtime_service import summarize_execute_runtime
from backend.app.services.issues_projection_service import rebuild_issue_index, sync_issue_states
from backend.app.services.process_state_service import update_process_state
from backend.app.services.session_service import create_session_record, mark_session_status, session_to_payload
from common.core.database import get_session_factory
from common.core.exceptions import ValidationError
from common.core.logger import logger
from common.core.request_context import apply_request_context, clear_request_context, copy_request_context, set_request_context

EXECUTE_RUNTIME_MANAGER = ExecutionManager()
EXECUTE_BACKGROUND_TASKS: dict[str, asyncio.Task[None]] = {}
EXECUTE_RUNTIME_KEYS: dict[str, str] = {}


# Execute Issues 进程服务负责执行开发合同、刷新 issues 状态，并推进卡片进入验收阶段。
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
    set_request_context(session_id=session_id, execution_process_id=execution_process_id, channel="issues")
    await write_execution_log(
        session,
        execution_process_id,
        stream=event.get("stream", "stdout"),
        event_type=event["event_type"],
        raw_text=event.get("raw_text"),
        payload=event.get("payload"),
    )
    await append_normalized_log_entry(session, session_id, event, execution_process_id=execution_process_id)
    await session.commit()
    logger.debug(
        "已持久化 execute 执行事件 session_id={} execution_process_id={} event_type={}",
        session_id,
        execution_process_id,
        event["event_type"],
    )


async def _finalize_execute_success(
    session: AsyncSession,
    card_id: str,
    session_id: str,
    execution_process_id: str,
    issues_path: str,
    exit_code: int | None,
) -> dict[str, Any]:
    logger.info(
        "开始收口 execute 成功结果 card_id={} session_id={} execution_process_id={} exit_code={}",
        card_id,
        session_id,
        execution_process_id,
        exit_code,
    )
    await rebuild_issue_index(session, card_id, issues_path)
    runtime = summarize_execute_runtime(issues_path)
    await advance_card_to_acceptance(session, card_id)
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
            active_process_type="skill_execute_issues",
            active_process_status="finished",
            active_process_session_id=session_id,
        ),
    )
    updated_card = await get_card_or_raise(session, card_id)
    return {
        "card_id": updated_card.id,
        "current_stage": updated_card.current_stage,
        "runtime": runtime,
        "execution_process": process_payload,
    }


async def _finalize_execute_failure(
    session: AsyncSession,
    card_id: str,
    session_id: str,
    execution_process_id: str | None,
    issues_path: str | None,
    reason: str,
    status: str = "failed",
    exit_code: int | None = None,
) -> dict[str, Any]:
    normalized_status = status if status in {"failed", "stopped", "aborted"} else "failed"
    logger.warning(
        "开始收口 execute 失败结果 card_id={} session_id={} execution_process_id={} status={} reason={}",
        card_id,
        session_id,
        execution_process_id,
        normalized_status,
        reason,
    )
    if issues_path:
        await rebuild_issue_index(session, card_id, issues_path)
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
            active_process_type="skill_execute_issues",
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


async def _run_execute_runtime(
    card_id: str,
    session_id: str,
    execution_process_id: str,
    runtime_execution_id: str,
    issues_path: str,
    request_context: dict[str, Any],
) -> None:
    factory = get_session_factory()
    apply_request_context(request_context)
    set_request_context(
        card_id=card_id,
        session_id=session_id,
        execution_process_id=execution_process_id,
        channel="issues",
        transport="runtime",
    )
    logger.info(
        "execute runtime 已启动 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
        card_id,
        session_id,
        execution_process_id,
        runtime_execution_id,
    )
    try:
        chunks = await EXECUTE_RUNTIME_MANAGER.collect(runtime_execution_id)
        async with factory() as session:
            for chunk in chunks:
                await _persist_execution_event(session, session_id, execution_process_id, chunk)
            await rebuild_issue_index(session, card_id, issues_path)

        result = await EXECUTE_RUNTIME_MANAGER.wait(runtime_execution_id)
        logger.info(
            "execute runtime 等待结束 runtime_execution_id={} status={} exit_code={}",
            runtime_execution_id,
            result.get("status"),
            result.get("exit_code"),
        )
        async with factory() as session:
            if result["status"] == "finished":
                await _finalize_execute_success(
                    session,
                    card_id,
                    session_id,
                    execution_process_id,
                    issues_path,
                    result.get("exit_code"),
                )
            else:
                await _persist_execution_event(
                    session,
                    session_id,
                    execution_process_id,
                    {
                        "event_type": "error",
                        "stream": "stderr",
                        "raw_text": f"execute process {result['status']}",
                        "payload": {"status": result["status"], "exit_code": result.get("exit_code")},
                    },
                )
                await _finalize_execute_failure(
                    session,
                    card_id,
                    session_id,
                    execution_process_id,
                    issues_path,
                    reason=f"execute process {result['status']}",
                    status=result["status"],
                    exit_code=result.get("exit_code"),
                )
    except Exception as exc:
        logger.exception(
            "execute runtime 执行失败 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
            card_id,
            session_id,
            execution_process_id,
            runtime_execution_id,
        )
        async with factory() as session:
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
            await _finalize_execute_failure(
                session,
                card_id,
                session_id,
                execution_process_id,
                issues_path,
                reason=str(exc),
                status="failed",
            )
    finally:
        EXECUTE_RUNTIME_KEYS.pop(execution_process_id, None)
        EXECUTE_BACKGROUND_TASKS.pop(execution_process_id, None)
        logger.info(
            "execute runtime 已清理 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
            card_id,
            session_id,
            execution_process_id,
            runtime_execution_id,
        )
        clear_request_context()


async def start_execute_process(session: AsyncSession, card_id: str) -> dict[str, Any]:
    set_request_context(card_id=card_id, channel="issues")
    logger.info("开始执行 execute 流程 card_id={}", card_id)
    precheck = await run_execute_precheck(session, card_id)
    session_record = await create_session_record(
        session,
        card_id,
        stage_key="contract",
        session_type="skill_execute_issues",
    )
    prompt = build_execute_issues_prompt(precheck)
    runtime_execution_id = f"execute-{session_record.id}"
    runtime = await EXECUTE_RUNTIME_MANAGER.start(runtime_execution_id, prompt)
    execution_process = await create_execution_process(
        session,
        session_record.id,
        run_reason="skill_execute_issues",
        executor_action={
            "command": runtime["command"],
            "prompt": prompt,
            "plan_path": precheck["plan_path"],
            "issues_path": precheck["issues_path"],
            "requirements_path": precheck["requirements_path"],
            "worktree": precheck["worktree"],
        },
        pid=runtime.get("pid"),
    )
    await rebuild_issue_index(session, card_id, precheck["issues_path"])
    await advance_card_to_developing(session, card_id)
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_execute_issues",
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
            "channel": "issues",
            "transport": "runtime",
        }
    )
    EXECUTE_RUNTIME_KEYS[execution_process["id"]] = runtime_execution_id
    EXECUTE_BACKGROUND_TASKS[execution_process["id"]] = asyncio.create_task(
        _run_execute_runtime(
            card_id,
            session_record.id,
            execution_process["id"],
            runtime_execution_id,
            precheck["issues_path"],
            request_context,
        )
    )
    updated_card = await get_card_or_raise(session, card_id)
    logger.info(
        "已调度 execute runtime 后台任务 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
        card_id,
        session_record.id,
        execution_process["id"],
        runtime_execution_id,
    )
    return {
        "precheck": precheck,
        "session": session_to_payload(session_record),
        "execution_process": execution_process,
        "current_stage": updated_card.current_stage,
        "prompt": prompt,
        "issues": sync_issue_states(precheck["issues_path"]),
    }


async def finish_execute_process(session: AsyncSession, card_id: str) -> dict[str, Any]:
    logger.info("开始手动完成 execute 流程 card_id={}", card_id)
    card = await get_card_or_raise(session, card_id)
    if card.active_process_type != "skill_execute_issues":
        raise ValidationError("当前卡片没有 execute-issues process")
    execution_process = await _latest_execution_process_payload(session, card.active_process_session_id)
    if execution_process is None or not card.issues_path:
        raise ValidationError("当前卡片缺少 execute-issues process 上下文")
    return await _finalize_execute_success(
        session,
        card_id,
        card.active_process_session_id,
        execution_process["id"],
        card.issues_path,
        execution_process.get("exit_code"),
    )


async def stop_execute_process(session: AsyncSession, card_id: str) -> dict[str, Any]:
    logger.warning("开始停止 execute 流程 card_id={}", card_id)
    card = await get_card_or_raise(session, card_id)
    if card.active_process_type != "skill_execute_issues":
        raise ValidationError("当前卡片没有运行中的 execute-issues process")
    if card.active_process_status != "running":
        raise ValidationError("只有运行中的 execute-issues process 才能停止")

    execution_process = await _latest_execution_process_payload(session, card.active_process_session_id)
    if execution_process is None:
        raise ValidationError("当前卡片缺少 execute process")

    runtime_execution_id = EXECUTE_RUNTIME_KEYS.get(execution_process["id"])
    if runtime_execution_id is not None:
        await EXECUTE_RUNTIME_MANAGER.interrupt(runtime_execution_id)
    task = EXECUTE_BACKGROUND_TASKS.get(execution_process["id"])
    if task is not None:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    await _persist_execution_event(
        session,
        card.active_process_session_id,
        execution_process["id"],
        {
            "event_type": "error",
            "stream": "stderr",
            "raw_text": "stopped by user",
            "payload": {"reason": "stopped by user"},
        },
    )
    return await _finalize_execute_failure(
        session,
        card_id,
        card.active_process_session_id,
        execution_process["id"],
        card.issues_path,
        reason="stopped by user",
        status="stopped",
    )


async def fail_execute_process(session: AsyncSession, card_id: str, reason: str) -> dict[str, Any]:
    if not reason.strip():
        raise ValidationError("Failure reason cannot be empty")
    logger.warning("开始标记 execute 流程失败 card_id={} reason={}", card_id, reason)
    card = await get_card_or_raise(session, card_id)
    if card.active_process_type != "skill_execute_issues":
        raise ValidationError("当前卡片没有 execute-issues process")

    execution_process = await _latest_execution_process_payload(session, card.active_process_session_id)
    if execution_process is None:
        raise ValidationError("当前卡片缺少 execute process")

    runtime_execution_id = EXECUTE_RUNTIME_KEYS.get(execution_process["id"])
    if runtime_execution_id is not None:
        await EXECUTE_RUNTIME_MANAGER.fail(runtime_execution_id, reason)
    task = EXECUTE_BACKGROUND_TASKS.get(execution_process["id"])
    if task is not None:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    await _persist_execution_event(
        session,
        card.active_process_session_id,
        execution_process["id"],
        {
            "event_type": "error",
            "stream": "stderr",
            "raw_text": reason,
            "payload": {"reason": reason},
        },
    )
    return await _finalize_execute_failure(
        session,
        card_id,
        card.active_process_session_id,
        execution_process["id"],
        card.issues_path,
        reason=reason,
        status="failed",
    )
