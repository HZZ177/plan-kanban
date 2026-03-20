from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.stage_service import update_card_stage


async def advance_card_to_contract(session: AsyncSession, card_id: str) -> dict:
    return await update_card_stage(session, card_id, "contract")


async def advance_card_to_acceptance(session: AsyncSession, card_id: str) -> dict:
    return await update_card_stage(session, card_id, "acceptance")


async def advance_card_to_developing(session: AsyncSession, card_id: str) -> dict:
    return await update_card_stage(session, card_id, "developing")


async def stop_card_in_developing(session: AsyncSession, card_id: str) -> dict:
    return await update_card_stage(session, card_id, "developing")
