from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.process_state import ProcessStateSchema
from backend.app.services.card_query_service import get_card_or_raise
from common.core.exceptions import ValidationError

ALLOWED_PROCESS_TYPES = {"none", "conversation", "skill_plan", "skill_execute_issues"}
ALLOWED_PROCESS_STATUSES = {"idle", "running", "finished", "failed"}


async def update_process_state(session: AsyncSession, card_id: str, payload: ProcessStateSchema) -> dict[str, str | None]:
    if payload.active_process_type not in ALLOWED_PROCESS_TYPES:
        raise ValidationError(f"Unsupported process type: {payload.active_process_type}")
    if payload.active_process_status not in ALLOWED_PROCESS_STATUSES:
        raise ValidationError(f"Unsupported process status: {payload.active_process_status}")

    card = await get_card_or_raise(session, card_id)
    card.active_process_type = payload.active_process_type
    card.active_process_status = payload.active_process_status
    card.active_process_session_id = payload.active_process_session_id

    await session.commit()
    await session.refresh(card)
    return {
        "active_process_type": card.active_process_type,
        "active_process_status": card.active_process_status,
        "active_process_session_id": card.active_process_session_id,
    }


async def get_process_state(session: AsyncSession, card_id: str) -> dict[str, str | None]:
    card = await get_card_or_raise(session, card_id)
    return {
        "active_process_type": card.active_process_type,
        "active_process_status": card.active_process_status,
        "active_process_session_id": card.active_process_session_id,
    }
