from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import card_to_detail_payload, get_card_or_raise
from backend.app.services.stage_transition_validator import validate_stage_transition


async def update_card_stage(session: AsyncSession, card_id: str, target_stage: str) -> dict[str, str | None]:
    card = await get_card_or_raise(session, card_id)
    validate_stage_transition(card.current_stage, target_stage)

    card.current_stage = target_stage
    if target_stage != "acceptance":
        card.acceptance_substate = None

    await session.commit()
    await session.refresh(card)
    return card_to_detail_payload(card)
