from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.chat_service import send_chat_message
from common.core.database import get_db_session

router = APIRouter(prefix="/cards", tags=["chat"])


class ChatRequestSchema(BaseModel):
    message: str = Field(min_length=1)
    session_id: str | None = None


@router.post("/{card_id}/chat")
async def send_chat_route(
    card_id: str,
    payload: ChatRequestSchema,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    return await send_chat_message(session, card_id, payload.message, payload.session_id)
