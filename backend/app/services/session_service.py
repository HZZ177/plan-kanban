from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from common.core.exceptions import NotFoundError, ValidationError
from common.models.session import SessionRecord

STAGE_DEFAULT_SESSION_TYPE_MAP = {
    "raw": "conversation",
    "plan": "conversation",
    "acceptance": "acceptance_review",
    "contract": "skill_execute_issues",
    "developing": "skill_execute_issues",
}

STAGE_ALLOWED_SESSION_TYPES = {
    "raw": {"conversation"},
    "plan": {"conversation", "skill_plan"},
    "acceptance": {"acceptance_review"},
    "contract": {"skill_execute_issues"},
    "developing": {"skill_execute_issues"},
}

SESSION_TYPE_STAGE_MAP = {
    "conversation": {"raw", "plan"},
    "skill_plan": {"plan"},
    "acceptance_review": {"acceptance"},
    "skill_execute_issues": {"contract", "developing"},
}


async def get_session_or_raise(session: AsyncSession, session_id: str) -> SessionRecord:
    session_record = await session.get(SessionRecord, session_id)
    if session_record is None:
        raise NotFoundError(f"Session not found: {session_id}")
    return session_record


def _validate_stage_session_type(stage_key: str, session_type: str) -> None:
    allowed_types = STAGE_ALLOWED_SESSION_TYPES.get(stage_key)
    if allowed_types is None:
        raise ValidationError(f"Unsupported session stage: {stage_key}")
    if session_type not in allowed_types:
        raise ValidationError(
            f"Invalid session type for stage {stage_key}: expected one of {sorted(allowed_types)}, got {session_type}"
        )

    allowed_stages = SESSION_TYPE_STAGE_MAP.get(session_type)
    if allowed_stages is None or stage_key not in allowed_stages:
        raise ValidationError(f"Session type {session_type} is not allowed in stage {stage_key}")


def session_to_payload(session_record: SessionRecord) -> dict[str, Any]:
    return {
        "id": session_record.id,
        "card_id": session_record.card_id,
        "stage_key": session_record.stage_key,
        "session_type": session_record.session_type,
        "cc_conversation_id": session_record.cc_conversation_id,
        "status": session_record.status,
        "started_at": session_record.started_at.isoformat() if session_record.started_at else None,
        "completed_at": session_record.completed_at.isoformat() if session_record.completed_at else None,
    }


async def create_session_record(
    session: AsyncSession,
    card_id: str,
    stage_key: str | None = None,
    session_type: str | None = None,
) -> SessionRecord:
    card = await get_card_or_raise(session, card_id)
    resolved_stage = stage_key or card.current_stage
    if resolved_stage not in STAGE_ALLOWED_SESSION_TYPES:
        raise ValidationError("Unsupported session stage")

    resolved_session_type = session_type or STAGE_DEFAULT_SESSION_TYPE_MAP[resolved_stage]
    _validate_stage_session_type(resolved_stage, resolved_session_type)

    session_record = SessionRecord(
        card_id=card.id,
        stage_key=resolved_stage,
        session_type=resolved_session_type,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    session.add(session_record)
    await session.flush()

    card.latest_session_id = session_record.id
    await session.commit()
    await session.refresh(session_record)
    return session_record


async def create_session(
    session: AsyncSession,
    card_id: str,
    stage_key: str | None = None,
    session_type: str | None = None,
) -> dict[str, Any]:
    session_record = await create_session_record(session, card_id, stage_key, session_type)
    return session_to_payload(session_record)


async def list_sessions(session: AsyncSession, card_id: str) -> list[dict[str, Any]]:
    await get_card_or_raise(session, card_id)
    result = await session.execute(
        select(SessionRecord).where(SessionRecord.card_id == card_id).order_by(SessionRecord.created_at.desc())
    )
    return [session_to_payload(item) for item in result.scalars().all()]
