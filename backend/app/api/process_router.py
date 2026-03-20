from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.process_state import ProcessStateSchema
from backend.app.services.execute_issues_process_service import stop_execute_process
from backend.app.services.process_state_service import get_process_state
from common.core.database import get_db_session

router = APIRouter(prefix="/cards", tags=["process"])


@router.get("/{card_id}/process", response_model=ProcessStateSchema)
async def get_process_state_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await get_process_state(session, card_id)


@router.post("/{card_id}/process/stop")
async def stop_execute_process_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await stop_execute_process(session, card_id)
