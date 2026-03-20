from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.card_create import CardCreateSchema
from backend.app.services.card_query_service import card_to_detail_payload
from common.models.card import Card


async def create_card(session: AsyncSession, payload: CardCreateSchema) -> dict[str, str | None]:
    card = Card(
        project_id=payload.project_id,
        title=payload.title,
        summary=payload.summary,
        owner=payload.owner,
        priority=payload.priority,
        raw_requirement=payload.raw_requirement,
    )
    session.add(card)
    await session.commit()
    await session.refresh(card)
    return card_to_detail_payload(card)
