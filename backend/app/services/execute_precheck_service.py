from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from common.core.exceptions import ValidationError


async def run_execute_precheck(session: AsyncSession, card_id: str) -> dict[str, str]:
    card = await get_card_or_raise(session, card_id)
    if card.current_stage != "contract":
        raise ValidationError("start-development 只能在 contract 阶段触发")
    if not card.plan_path or not Path(card.plan_path).exists():
        raise ValidationError("Plan file not found for current card")
    if not card.issues_path or not Path(card.issues_path).exists():
        raise ValidationError("Issues CSV not found for current card")
    return {
        "card_id": card.id,
        "plan_path": card.plan_path,
        "issues_path": card.issues_path,
        "current_stage": card.current_stage,
    }
