from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.history_recovery_service import build_recovery_snapshot
from common.core.database import get_db_session

router = APIRouter(tags=["recovery"])


@router.get("/cards/{card_id}/recovery/{session_id}")
async def recovery_snapshot_route(card_id: str, session_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await build_recovery_snapshot(session, card_id, session_id)
