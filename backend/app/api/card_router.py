from __future__ import annotations

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.acceptance_substate import AcceptanceSubstateSchema
from backend.app.schemas.card_create import CardCreateSchema
from backend.app.schemas.card_detail import CardDetailSchema
from backend.app.schemas.card_update import CardUpdateSchema
from backend.app.services.acceptance_substate_service import update_acceptance_substate
from backend.app.services.card_create_service import create_card
from backend.app.services.card_query_service import get_card_detail, list_cards
from backend.app.services.card_update_service import update_card
from backend.app.services.stage_service import update_card_stage
from common.core.database import get_db_session

router = APIRouter(prefix="/cards", tags=["cards"])


class CardStageUpdateSchema(BaseModel):
    current_stage: str = Field(min_length=1)


@router.get("", response_model=list[CardDetailSchema])
async def list_card_route(session: AsyncSession = Depends(get_db_session)) -> list[dict]:
    return await list_cards(session)


@router.get("/{card_id}", response_model=CardDetailSchema)
async def get_card_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await get_card_detail(session, card_id)


@router.post("", response_model=CardDetailSchema, status_code=status.HTTP_201_CREATED)
async def create_card_route(payload: CardCreateSchema, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await create_card(session, payload)


@router.put("/{card_id}", response_model=CardDetailSchema)
async def update_card_route(card_id: str, payload: CardUpdateSchema, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await update_card(session, card_id, payload)


@router.put("/{card_id}/stage", response_model=CardDetailSchema)
async def update_card_stage_route(
    card_id: str,
    payload: CardStageUpdateSchema,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    return await update_card_stage(session, card_id, payload.current_stage)


@router.put("/{card_id}/acceptance-substate", response_model=AcceptanceSubstateSchema)
async def update_acceptance_substate_route(
    card_id: str,
    payload: AcceptanceSubstateSchema,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    return await update_acceptance_substate(session, card_id, payload.acceptance_substate)
