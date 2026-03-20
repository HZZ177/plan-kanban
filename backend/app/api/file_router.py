from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.file_watch_service import poll_stage_files
from backend.app.services.stage_file_service import list_stage_files, read_stage_file
from common.core.database import get_db_session

router = APIRouter(prefix="/cards", tags=["files"])


@router.get("/{card_id}/files")
async def list_stage_files_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> list[dict]:
    return await list_stage_files(session, card_id)


@router.get("/{card_id}/files/content")
async def read_stage_file_route(
    card_id: str,
    file_path: str = Query(...),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    return await read_stage_file(session, card_id, file_path)


@router.get("/{card_id}/files/watch")
async def watch_stage_files_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await poll_stage_files(session, card_id)
