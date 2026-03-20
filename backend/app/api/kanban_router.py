from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.kanban_projection_service import get_kanban_projection
from common.core.database import get_db_session

router = APIRouter(tags=["kanban"])


@router.get("/kanban")
async def get_kanban_route(session: AsyncSession = Depends(get_db_session)) -> dict:
    return await get_kanban_projection(session)
