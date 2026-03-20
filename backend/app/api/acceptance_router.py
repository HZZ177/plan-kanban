from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.acceptance_service import build_acceptance_summary, rollback_acceptance
from common.core.database import get_db_session

router = APIRouter(prefix="/cards", tags=["acceptance"])


@router.get("/{card_id}/acceptance")
async def acceptance_summary_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await build_acceptance_summary(session, card_id)


@router.post("/{card_id}/acceptance/rollback")
async def acceptance_rollback_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await rollback_acceptance(session, card_id)
