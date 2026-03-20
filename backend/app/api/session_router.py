from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.session_history_service import list_card_sessions, list_session_entries
from common.core.database import get_db_session

router = APIRouter(tags=["sessions"])


@router.get("/cards/{card_id}/sessions")
async def list_card_sessions_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> list[dict]:
    return await list_card_sessions(session, card_id)


@router.get("/sessions/{session_id}/entries")
async def list_session_entries_route(session_id: str, session: AsyncSession = Depends(get_db_session)) -> list[dict]:
    return await list_session_entries(session, session_id)
