from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.process_state import ProcessStateSchema
from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.card_transition_service import advance_card_to_acceptance, advance_card_to_developing
from backend.app.services.execute_issues_prompt_builder import build_execute_issues_prompt
from backend.app.services.execute_precheck_service import run_execute_precheck
from backend.app.services.issue_runtime_service import summarize_execute_runtime
from backend.app.services.process_state_service import update_process_state
from backend.app.services.session_service import create_session_record, session_to_payload
from common.core.exceptions import ValidationError


async def start_execute_process(session: AsyncSession, card_id: str) -> dict[str, Any]:
    precheck = await run_execute_precheck(session, card_id)
    card = await get_card_or_raise(session, card_id)
    session_record = await create_session_record(session, card_id, stage_key="contract", session_type="skill_execute_issues")
    await advance_card_to_developing(session, card_id)
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_execute_issues",
            active_process_status="running",
            active_process_session_id=session_record.id,
        ),
    )
    updated_card = await get_card_or_raise(session, card_id)
    return {
        "precheck": precheck,
        "session": session_to_payload(session_record),
        "current_stage": updated_card.current_stage,
        "prompt": build_execute_issues_prompt(updated_card, precheck["plan_path"], precheck["issues_path"]),
    }


async def finish_execute_process(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    if not card.issues_path:
        raise ValidationError("Issues CSV not found for current card")
    runtime = summarize_execute_runtime(card.issues_path)
    await advance_card_to_acceptance(session, card_id)
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_execute_issues",
            active_process_status="finished",
            active_process_session_id=card.active_process_session_id,
        ),
    )
    updated_card = await get_card_or_raise(session, card_id)
    return {
        "card_id": updated_card.id,
        "current_stage": updated_card.current_stage,
        "runtime": runtime,
    }


async def stop_execute_process(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    if card.active_process_type != "skill_execute_issues":
        raise ValidationError("当前卡片没有运行中的 execute-issues process")
    if card.active_process_status != "running":
        raise ValidationError("只有运行中的 execute-issues process 才能停止")
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_execute_issues",
            active_process_status="failed",
            active_process_session_id=card.active_process_session_id,
        ),
    )
    refreshed = await get_card_or_raise(session, card_id)
    return {
        "card_id": refreshed.id,
        "current_stage": refreshed.current_stage,
        "active_process_type": refreshed.active_process_type,
        "active_process_status": refreshed.active_process_status,
    }


async def fail_execute_process(session: AsyncSession, card_id: str, reason: str) -> dict[str, Any]:
    if not reason.strip():
        raise ValidationError("Failure reason cannot be empty")
    card = await get_card_or_raise(session, card_id)
    if card.active_process_type != "skill_execute_issues":
        raise ValidationError("当前卡片没有 execute-issues process")
    await update_process_state(
        session,
        card_id,
        ProcessStateSchema(
            active_process_type="skill_execute_issues",
            active_process_status="failed",
            active_process_session_id=card.active_process_session_id,
        ),
    )
    refreshed = await get_card_or_raise(session, card_id)
    return {
        "card_id": refreshed.id,
        "current_stage": refreshed.current_stage,
        "active_process_type": refreshed.active_process_type,
        "active_process_status": refreshed.active_process_status,
        "reason": reason,
    }
