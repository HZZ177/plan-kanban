from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.conversation_entry_service import list_conversation_entries
from backend.app.services.session_service import list_sessions


async def list_card_sessions(session: AsyncSession, card_id: str) -> list[dict[str, Any]]:
    return await list_sessions(session, card_id)


async def list_session_entries(session: AsyncSession, session_id: str) -> list[dict[str, Any]]:
    return await list_conversation_entries(session, session_id)
