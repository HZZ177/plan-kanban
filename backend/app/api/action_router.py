from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.execute_issues_process_service import fail_execute_process, finish_execute_process, start_execute_process
from backend.app.services.execute_precheck_service import run_execute_precheck
from backend.app.services.plan_precheck_service import run_plan_precheck
from backend.app.services.plan_process_service import fail_plan_process, finish_plan_process, start_plan_process
from common.core.database import get_db_session

router = APIRouter(prefix="/actions", tags=["actions"])


class PlanFailureSchema(BaseModel):
    reason: str = Field(min_length=1)


class ExecuteFailureSchema(BaseModel):
    reason: str = Field(min_length=1)


@router.post("/cards/{card_id}/generate-contract/precheck")
async def generate_contract_precheck_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await run_plan_precheck(session, card_id)


@router.post("/cards/{card_id}/generate-contract")
async def generate_contract_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    await start_plan_process(session, card_id)
    return await finish_plan_process(session, card_id)


@router.post("/cards/{card_id}/generate-contract/fail")
async def generate_contract_fail_route(
    card_id: str,
    payload: PlanFailureSchema,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    return await fail_plan_process(session, card_id, payload.reason)


@router.post("/cards/{card_id}/start-development/precheck")
async def start_development_precheck_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    return await run_execute_precheck(session, card_id)


@router.post("/cards/{card_id}/start-development")
async def start_development_route(card_id: str, session: AsyncSession = Depends(get_db_session)) -> dict:
    await start_execute_process(session, card_id)
    return await finish_execute_process(session, card_id)


@router.post("/cards/{card_id}/start-development/fail")
async def start_development_fail_route(
    card_id: str,
    payload: ExecuteFailureSchema,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    return await fail_execute_process(session, card_id, payload.reason)
