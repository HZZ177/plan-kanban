from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.diff_service import get_single_file_diff, list_changed_files
from common.core.database import get_db_session

router = APIRouter(prefix="/cards", tags=["diff"])


@router.get("/{card_id}/diff/files")
async def list_changed_files_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> list[dict]:
    return await list_changed_files(session, card_id)


@router.get("/{card_id}/diff/file")
async def single_file_diff_route(
    card_id: str,
    file_path: str = Query(...),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    return await get_single_file_diff(session, card_id, file_path)
