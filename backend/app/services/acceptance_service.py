from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.card_transition_service import advance_card_to_developing
from backend.app.services.diff_service import get_single_file_diff, list_changed_files


async def build_acceptance_summary(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    changed_files = await list_changed_files(session, card_id)
    preview = None
    if changed_files:
        preview = await get_single_file_diff(session, card_id, changed_files[0]["path"])
    return {
        "card_id": card.id,
        "current_stage": card.current_stage,
        "changed_files": changed_files,
        "preview": preview,
        "acceptance_substate": card.acceptance_substate,
    }


async def rollback_acceptance(session: AsyncSession, card_id: str) -> dict[str, Any]:
    return await advance_card_to_developing(session, card_id)
