from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.card_update import CardUpdateSchema
from backend.app.services.card_query_service import card_to_detail_payload, get_card_or_raise


async def update_card(session: AsyncSession, card_id: str, payload: CardUpdateSchema) -> dict[str, str | None]:
    card = await get_card_or_raise(session, card_id)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(card, field, value)

    await session.commit()
    await session.refresh(card)
    return card_to_detail_payload(card)
