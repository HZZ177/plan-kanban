from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.chat_context_builder import build_chat_context
from backend.app.services.conversation_entry_service import (
    conversation_entry_to_payload,
    create_conversation_entry,
    list_conversation_entries,
)
from backend.app.services.session_service import create_session_record, get_session_or_raise, session_to_payload
from common.core.exceptions import ValidationError


async def send_chat_message(
    session: AsyncSession,
    card_id: str,
    message: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    if not message.strip():
        raise ValidationError("Message cannot be empty")

    card = await get_card_or_raise(session, card_id)
    context = build_chat_context(card)

    if session_id is None:
        session_record = await create_session_record(session, card_id, stage_key=card.current_stage)
    else:
        session_record = await get_session_or_raise(session, session_id)
        if session_record.card_id != card_id:
            raise ValidationError("Session does not belong to the specified card")

    card.active_process_type = "conversation"
    card.active_process_status = "running"
    card.active_process_session_id = session_record.id
    card.latest_session_id = session_record.id
    await session.flush()

    user_entry = await create_conversation_entry(
        session,
        session_record.id,
        entry_type="user_message",
        role="user",
        content=message,
        payload={"stage_key": card.current_stage},
    )
    assistant_text = f"已记录{context['stage_label']}阶段消息，并保留当前阶段语义用于后续对话。"
    assistant_entry = await create_conversation_entry(
        session,
        session_record.id,
        entry_type="assistant_text",
        role="assistant",
        content=assistant_text,
        payload={"context": context},
    )

    session_record.status = "completed"
    card.active_process_status = "finished"
    await session.commit()
    await session.refresh(session_record)
    await session.refresh(card)

    return {
        "session": session_to_payload(session_record),
        "context": context,
        "entries": [
            conversation_entry_to_payload(user_entry),
            conversation_entry_to_payload(assistant_entry),
        ],
    }


async def get_chat_history(session: AsyncSession, session_id: str) -> list[dict[str, Any]]:
    await get_session_or_raise(session, session_id)
    return await list_conversation_entries(session, session_id)
