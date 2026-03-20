from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from common.core.exceptions import ValidationError

ALLOWED_ACCEPTANCE_SUBSTATES = {"测试中", "测试失败", "审查中", "已验收", "已打回"}


async def update_acceptance_substate(session: AsyncSession, card_id: str, acceptance_substate: str | None) -> dict[str, str | None]:
    card = await get_card_or_raise(session, card_id)
    if card.current_stage != "acceptance":
        raise ValidationError("Acceptance substate can only be updated in acceptance stage")
    if acceptance_substate is not None and acceptance_substate not in ALLOWED_ACCEPTANCE_SUBSTATES:
        raise ValidationError(f"Unsupported acceptance substate: {acceptance_substate}")

    card.acceptance_substate = acceptance_substate
    await session.commit()
    await session.refresh(card)
    return {"acceptance_substate": card.acceptance_substate}
