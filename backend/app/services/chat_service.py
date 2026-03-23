from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.runtime.execution_manager import ExecutionManager
from backend.app.runtime.log_normalizer import normalize_log_event
from backend.app.schemas.process_state import ProcessStateSchema
from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.chat_context_builder import build_chat_context
from backend.app.services.conversation_entry_service import (
    conversation_entry_to_payload,
    create_conversation_entry,
    list_conversation_entries,
    merge_conversation_entry,
)
from backend.app.services.event_publish_service import publish_channel_event
from backend.app.services.execution_log_service import write_execution_log
from backend.app.services.execution_process_service import create_execution_process, update_execution_process_status
from backend.app.services.process_state_service import update_process_state
from backend.app.services.session_service import create_session_record, get_session_or_raise, mark_session_status, session_to_payload
from backend.app.ws.event_schema import build_ws_event
from common.core.database import get_session_factory
from common.core.exceptions import ValidationError
from common.core.logger import logger
from common.core.request_context import apply_request_context, clear_request_context, copy_request_context, set_request_context

CHAT_RUNTIME_MANAGER = ExecutionManager()
CHAT_PROMPT_HISTORY_LIMIT = 20
CHAT_BACKGROUND_TASKS: dict[str, asyncio.Task[None]] = {}
CHAT_RUNTIME_KEYS: dict[str, str] = {}


# 聊天服务负责把用户消息、Claude runtime 输出与 conversation 频道推送串成一条完整链路。
async def append_normalized_log_entry(
    session: AsyncSession,
    session_id: str,
    event: dict[str, Any],
    execution_process_id: str | None = None,
) -> dict[str, Any] | None:
    normalized = normalize_log_event(event)
    if normalized is None:
        return None
    entry = await merge_conversation_entry(
        session,
        session_id,
        entry_type=normalized["entry_type"],
        role=normalized["role"],
        content=normalized.get("content"),
        payload=normalized.get("payload"),
        execution_process_id=execution_process_id,
        merge_key=normalized.get("merge_key"),
    )
    await session.flush()
    logger.debug(
        "已追加标准化日志条目 session_id={} execution_process_id={} entry_type={}",
        session_id,
        execution_process_id,
        normalized["entry_type"],
    )
    return conversation_entry_to_payload(entry)


async def publish_conversation_event(card_id: str, session_id: str, entry: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {
        "card_id": card_id,
        "session_id": session_id,
    }
    if entry is not None:
        payload["entry"] = entry
    set_request_context(card_id=card_id, session_id=session_id, channel="conversation")
    logger.debug("开始发布对话事件 card_id={} session_id={} has_entry={}", card_id, session_id, entry is not None)
    await publish_channel_event("conversation", build_ws_event("conversation.delta", "conversation", payload))


def _stringify_history_entry(entry: dict[str, Any]) -> str:
    label = str(entry.get("role") or entry.get("entry_type") or "assistant")
    content = str(entry.get("content") or "").strip()
    if not content:
        payload = entry.get("payload")
        if payload is not None:
            content = str(payload)
    return f"[{label}] {content}".strip()


def build_chat_prompt(context: dict[str, Any], history_entries: list[dict[str, Any]], message: str) -> str:
    recent_history = history_entries[-CHAT_PROMPT_HISTORY_LIMIT:]
    history_block = "\n".join(_stringify_history_entry(entry) for entry in recent_history if entry.get("content") or entry.get("payload"))
    file_hints = ", ".join(str(item) for item in context.get("file_hints") or [])

    sections = [
        "你正在 Plan Kanban 工作台中处理一条普通对话消息。",
        "请基于下面的卡片上下文回答用户，保持回答直接、清晰，优先结合当前阶段目标。",
        "",
        "卡片上下文：",
        f"- card_id: {context.get('card_id')}",
        f"- stage_key: {context.get('stage_key')}",
        f"- stage_label: {context.get('stage_label')}",
        f"- title: {context.get('title')}",
        f"- raw_requirement: {context.get('raw_requirement')}",
        f"- plan_path: {context.get('plan_path') or '无'}",
        f"- issues_path: {context.get('issues_path') or '无'}",
        f"- file_hints: {file_hints or '无'}",
        f"- workspace_focus: {context.get('workspace_focus') or '无'}",
    ]

    if history_block:
        sections.extend([
            "",
            "最近会话历史（按时间正序）：",
            history_block,
        ])

    sections.extend(
        [
            "",
            "当前用户消息：",
            message,
        ]
    )
    return "\n".join(sections)


async def _persist_chat_runtime_event(
    session: AsyncSession,
    card_id: str,
    session_id: str,
    execution_process_id: str,
    event: dict[str, Any],
) -> dict[str, Any]:
    set_request_context(
        card_id=card_id,
        session_id=session_id,
        execution_process_id=execution_process_id,
        channel="conversation",
    )
    await write_execution_log(
        session,
        execution_process_id,
        stream=event.get("stream", "stdout"),
        event_type=event["event_type"],
        raw_text=event.get("raw_text"),
        payload=event.get("payload"),
    )
    entry = await append_normalized_log_entry(
        session,
        session_id,
        event,
        execution_process_id=execution_process_id,
    )
    await session.commit()
    logger.debug(
        "聊天事件持久化结果 card_id={} session_id={} execution_process_id={} event_type={} has_entry={} entry_id={} entry_type={} content_len={}",
        card_id,
        session_id,
        execution_process_id,
        event.get("event_type"),
        entry is not None,
        entry.get("id") if entry else None,
        entry.get("entry_type") if entry else None,
        len(entry.get("content") or "") if entry else 0,
    )
    if entry is not None:
        await publish_conversation_event(card_id, session_id, entry)
    return entry


async def _finalize_chat_success(
    session: AsyncSession,
    card_id: str,
    session_id: str,
    execution_process_id: str,
    exit_code: int | None,
) -> None:
    logger.info(
        "Finalizing chat success card_id={} session_id={} execution_process_id={} exit_code={}",
        card_id,
        session_id,
        execution_process_id,
        exit_code,
    )
    await update_execution_process_status(
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
            active_process_type="conversation",
            active_process_status="finished",
            active_process_session_id=session_id,
        ),
    )


async def _finalize_chat_failure(
    session: AsyncSession,
    card_id: str,
    session_id: str,
    execution_process_id: str | None,
    reason: str,
    *,
    status: str = "failed",
    exit_code: int | None = None,
    persist_error_entry: bool = True,
) -> None:
    normalized_status = status if status in {"failed", "stopped", "aborted"} else "failed"
    logger.warning(
        "Finalizing chat failure card_id={} session_id={} execution_process_id={} status={} reason={}",
        card_id,
        session_id,
        execution_process_id,
        normalized_status,
        reason,
    )
    if execution_process_id is not None:
        await update_execution_process_status(
            session,
            execution_process_id,
            normalized_status,
            exit_code=exit_code,
            last_error=reason,
            dropped=True,
        )
    if persist_error_entry:
        event = {
            "event_type": "error",
            "stream": "stderr",
            "raw_text": reason,
            "payload": {"reason": reason, "status": normalized_status, "exit_code": exit_code},
        }
        if execution_process_id is not None:
            await _persist_chat_runtime_event(session, card_id, session_id, execution_process_id, event)
        else:
            entry = await append_normalized_log_entry(
                session,
                session_id,
                event,
                execution_process_id=execution_process_id,
            )
            await session.commit()
            await publish_conversation_event(card_id, session_id, entry)
    await mark_session_status(session, session_id, "failed")
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="conversation",
            active_process_status="failed",
            active_process_session_id=session_id,
        ),
    )


async def _run_chat_runtime(
    card_id: str,
    session_id: str,
    execution_process_id: str,
    runtime_execution_id: str,
    request_context: dict[str, Any],
) -> None:
    factory = get_session_factory()
    saw_error_chunk = False
    apply_request_context(request_context)
    set_request_context(
        card_id=card_id,
        session_id=session_id,
        execution_process_id=execution_process_id,
        channel="conversation",
        transport="runtime",
    )
    logger.info(
        "聊天 runtime 已启动 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
        card_id,
        session_id,
        execution_process_id,
        runtime_execution_id,
    )
    try:
        async for chunk in CHAT_RUNTIME_MANAGER.stream(runtime_execution_id):
            saw_error_chunk = saw_error_chunk or chunk.get("event_type") in {"error", "stderr"}
            async with factory() as session:
                await _persist_chat_runtime_event(session, card_id, session_id, execution_process_id, chunk)

        result = await CHAT_RUNTIME_MANAGER.wait(runtime_execution_id)
        logger.info(
            "聊天 runtime 等待结束 runtime_execution_id={} status={} exit_code={}",
            runtime_execution_id,
            result.get("status"),
            result.get("exit_code"),
        )
        async with factory() as session:
            if result["status"] == "finished":
                await _finalize_chat_success(
                    session,
                    card_id,
                    session_id,
                    execution_process_id,
                    result.get("exit_code"),
                )
            else:
                failure_reason = f"conversation process {result['status']}"
                if not saw_error_chunk:
                    await _persist_chat_runtime_event(
                        session,
                        card_id,
                        session_id,
                        execution_process_id,
                        {
                            "event_type": "error",
                            "stream": "stderr",
                            "raw_text": failure_reason,
                            "payload": {"status": result["status"], "exit_code": result.get("exit_code")},
                        },
                    )
                await _finalize_chat_failure(
                    session,
                    card_id,
                    session_id,
                    execution_process_id,
                    failure_reason,
                    status=result["status"],
                    exit_code=result.get("exit_code"),
                    persist_error_entry=False,
                )
    except Exception as exc:
        logger.exception(
            "聊天 runtime 执行失败 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
            card_id,
            session_id,
            execution_process_id,
            runtime_execution_id,
        )
        async with factory() as session:
            await _finalize_chat_failure(
                session,
                card_id,
                session_id,
                execution_process_id,
                str(exc),
                persist_error_entry=True,
            )
    finally:
        CHAT_RUNTIME_KEYS.pop(execution_process_id, None)
        CHAT_BACKGROUND_TASKS.pop(execution_process_id, None)
        logger.info(
            "聊天 runtime 已清理 card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
            card_id,
            session_id,
            execution_process_id,
            runtime_execution_id,
        )
        clear_request_context()


async def send_chat_message(
    session: AsyncSession,
    card_id: str,
    message: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    if not message.strip():
        raise ValidationError("Message cannot be empty")

    set_request_context(card_id=card_id, channel="conversation")
    logger.info("Sending chat message card_id={} session_id={} message_length={}", card_id, session_id, len(message))

    card = await get_card_or_raise(session, card_id)
    context = build_chat_context(card)

    if session_id is None:
        session_record = await create_session_record(session, card_id, stage_key=card.current_stage)
    else:
        session_record = await get_session_or_raise(session, session_id)
        if session_record.card_id != card_id:
            raise ValidationError("Session does not belong to the specified card")
        session_record.status = "running"
        session_record.completed_at = None
        await session.commit()
        await session.refresh(session_record)
        logger.info("Reusing session record session_id={} card_id={}", session_record.id, card_id)

    history_entries = await list_conversation_entries(session, session_record.id)

    card.latest_session_id = session_record.id
    await session.commit()
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="conversation",
            active_process_status="running",
            active_process_session_id=session_record.id,
        ),
    )

    user_entry = await create_conversation_entry(
        session,
        session_record.id,
        entry_type="user_message",
        role="user",
        content=message,
        payload={"stage_key": card.current_stage, "context": context},
    )
    await session.commit()
    user_entry_payload = conversation_entry_to_payload(user_entry)
    await publish_conversation_event(card_id, session_record.id, user_entry_payload)

    prompt = build_chat_prompt(context, history_entries, message)
    runtime_execution_id = f"conversation-{session_record.id}-{user_entry.id}"
    execution_process_id: str | None = None

    try:
        runtime = await CHAT_RUNTIME_MANAGER.start(runtime_execution_id, prompt)
        execution_process = await create_execution_process(
            session,
            session_record.id,
            run_reason="conversation",
            executor_action={
                "command": runtime["command"],
                "prompt": prompt,
                "context": context,
                "message": message,
            },
            pid=runtime.get("pid"),
        )
        execution_process_id = execution_process["id"]
        request_context = copy_request_context()
        request_context.update(
            {
                "card_id": card_id,
                "session_id": session_record.id,
                "execution_process_id": execution_process_id,
                "channel": "conversation",
                "transport": "runtime",
            }
        )
        CHAT_RUNTIME_KEYS[execution_process_id] = runtime_execution_id
        CHAT_BACKGROUND_TASKS[execution_process_id] = asyncio.create_task(
            _run_chat_runtime(card_id, session_record.id, execution_process_id, runtime_execution_id, request_context)
        )
        logger.info(
            "Chat runtime task scheduled card_id={} session_id={} execution_process_id={} runtime_execution_id={}",
            card_id,
            session_record.id,
            execution_process_id,
            runtime_execution_id,
        )
        return {
            "session": session_to_payload(session_record),
            "context": context,
            "entries": await list_conversation_entries(session, session_record.id),
        }
    except Exception as exc:
        logger.exception("Failed to send chat message card_id={} session_id={}", card_id, session_record.id)
        await _finalize_chat_failure(
            session,
            card_id,
            session_record.id,
            execution_process_id,
            str(exc),
            persist_error_entry=True,
        )
        raise


async def get_chat_history(session: AsyncSession, session_id: str) -> list[dict[str, Any]]:
    await get_session_or_raise(session, session_id)
    entries = await list_conversation_entries(session, session_id)
    logger.debug("Loaded chat history session_id={} count={}", session_id, len(entries))
    return entries
