from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.session_service import get_session_or_raise
from common.models.conversation_entry import ConversationEntry

ALLOWED_ENTRY_TYPES = {
    "user_message",
    "assistant_text",
    "tool_use",
    "tool_result",
    "thinking",
    "error",
    "summary",
}


# 会话条目服务负责持久化聊天消息，并支持同一 assistant 回复的增量合并。
def conversation_entry_to_payload(entry: ConversationEntry) -> dict[str, Any]:
    return {
        "id": entry.id,
        "session_id": entry.session_id,
        "execution_process_id": entry.execution_process_id,
        "entry_type": entry.entry_type,
        "role": entry.role,
        "content": entry.content,
        "payload": entry.payload,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None,
    }


async def create_conversation_entry(
    session: AsyncSession,
    session_id: str,
    entry_type: str,
    role: str,
    content: str | None = None,
    payload: dict[str, Any] | None = None,
    execution_process_id: str | None = None,
) -> ConversationEntry:
    await get_session_or_raise(session, session_id)
    if entry_type not in ALLOWED_ENTRY_TYPES:
        raise ValueError(f"Unsupported conversation entry type: {entry_type}")

    next_order_index = (
        await session.scalar(
            select(func.coalesce(func.max(ConversationEntry.order_index), 0) + 1).where(
                ConversationEntry.session_id == session_id
            )
        )
    )
    now = datetime.now(timezone.utc)
    entry = ConversationEntry(
        session_id=session_id,
        execution_process_id=execution_process_id,
        entry_type=entry_type,
        order_index=int(next_order_index or 1),
        role=role,
        content=content,
        payload=payload,
        created_at=now,
        updated_at=now,
    )
    session.add(entry)
    await session.flush()
    return entry


async def merge_conversation_entry(
    session: AsyncSession,
    session_id: str,
    entry_type: str,
    role: str,
    content: str | None = None,
    payload: dict[str, Any] | None = None,
    execution_process_id: str | None = None,
    merge_key: str | None = None,
) -> ConversationEntry:
    if not merge_key:
        return await create_conversation_entry(
            session,
            session_id,
            entry_type=entry_type,
            role=role,
            content=content,
            payload=payload,
            execution_process_id=execution_process_id,
        )

    result = await session.execute(
        select(ConversationEntry)
        .where(
            ConversationEntry.session_id == session_id,
            ConversationEntry.execution_process_id == execution_process_id,
            ConversationEntry.entry_type == entry_type,
        )
        .order_by(ConversationEntry.created_at.desc(), ConversationEntry.id.desc())
        .limit(1)
    )
    existing = result.scalar_one_or_none()
    existing_merge_key = existing.payload.get("merge_key") if existing and isinstance(existing.payload, dict) else None
    if existing is not None and existing_merge_key == merge_key:
        existing.content = content
        existing.payload = payload
        existing.updated_at = datetime.now(timezone.utc)
        await session.flush()
        return existing

    return await create_conversation_entry(
        session,
        session_id,
        entry_type=entry_type,
        role=role,
        content=content,
        payload=payload,
        execution_process_id=execution_process_id,
    )


async def list_conversation_entries(session: AsyncSession, session_id: str) -> list[dict[str, Any]]:
    await get_session_or_raise(session, session_id)
    result = await session.execute(
        select(ConversationEntry)
        .where(ConversationEntry.session_id == session_id)
        .order_by(ConversationEntry.order_index.asc(), ConversationEntry.created_at.asc(), ConversationEntry.id.asc())
    )
    return [conversation_entry_to_payload(item) for item in result.scalars().all()]
