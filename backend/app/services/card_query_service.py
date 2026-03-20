from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.core.exceptions import NotFoundError
from common.models.card import Card


def card_to_detail_payload(card: Card) -> dict[str, Any]:
    return {
        "id": card.id,
        "project_id": card.project_id,
        "title": card.title,
        "summary": card.summary,
        "owner": card.owner,
        "priority": card.priority,
        "raw_requirement": card.raw_requirement,
        "current_stage": card.current_stage,
        "acceptance_substate": card.acceptance_substate,
        "plan_path": card.plan_path,
        "issues_path": card.issues_path,
        "active_process_type": card.active_process_type,
        "active_process_status": card.active_process_status,
        "active_process_session_id": card.active_process_session_id,
    }


async def list_cards(session: AsyncSession) -> list[dict[str, Any]]:
    result = await session.execute(select(Card).where(Card.archived.is_(False)).order_by(Card.sort_order.asc(), Card.created_at.asc()))
    return [card_to_detail_payload(card) for card in result.scalars().all()]


async def get_card_or_raise(session: AsyncSession, card_id: str) -> Card:
    card = await session.get(Card, card_id)
    if card is None or card.archived:
        raise NotFoundError(f"Card not found: {card_id}")
    return card


async def get_card_detail(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    return card_to_detail_payload(card)
