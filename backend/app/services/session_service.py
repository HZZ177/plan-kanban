from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.core.exceptions import NotFoundError, ValidationError
from common.core.logger import logger
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

RUN_REASON_SESSION_TYPE_MAP = {
    "conversation": "conversation",
    "skill_plan": "skill_plan",
    "skill_execute_issues": "skill_execute_issues",
    "review": "acceptance_review",
    "test": "skill_execute_issues",
}


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


# 会话服务负责创建、复用和结束不同阶段的会话记录。
async def get_session_or_raise(session: AsyncSession, session_id: str) -> SessionRecord:
    session_record = await session.get(SessionRecord, session_id)
    if session_record is None:
        logger.warning("未找到会话 session_id={}", session_id)
        raise NotFoundError(f"Session not found: {session_id}")
    return session_record


async def create_session_record(
    session: AsyncSession,
    card_id: str,
    stage_key: str | None = None,
    session_type: str | None = None,
    cc_conversation_id: str | None = None,
) -> SessionRecord:
    from backend.app.services.card_query_service import get_card_or_raise

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
        cc_conversation_id=cc_conversation_id,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    session.add(session_record)
    await session.flush()

    card.latest_session_id = session_record.id
    await session.commit()
    await session.refresh(session_record)
    logger.info(
        "已创建会话记录 session_id={} card_id={} stage_key={} session_type={}",
        session_record.id,
        card_id,
        resolved_stage,
        resolved_session_type,
    )
    return session_record


async def create_session(
    session: AsyncSession,
    card_id: str,
    stage_key: str | None = None,
    session_type: str | None = None,
    cc_conversation_id: str | None = None,
) -> dict[str, Any]:
    session_record = await create_session_record(session, card_id, stage_key, session_type, cc_conversation_id)
    return session_to_payload(session_record)


async def bind_execution_session(
    session: AsyncSession,
    card_id: str,
    run_reason: str,
    stage_key: str | None = None,
    cc_conversation_id: str | None = None,
) -> SessionRecord:
    session_type = RUN_REASON_SESSION_TYPE_MAP.get(run_reason)
    if session_type is None:
        raise ValidationError(f"Unsupported run reason for session binding: {run_reason}")
    logger.info(
        "准备绑定执行会话 card_id={} run_reason={} stage_key={} session_type={}",
        card_id,
        run_reason,
        stage_key,
        session_type,
    )
    return await create_session_record(
        session,
        card_id,
        stage_key=stage_key,
        session_type=session_type,
        cc_conversation_id=cc_conversation_id,
    )


async def mark_session_status(session: AsyncSession, session_id: str, status: str) -> dict[str, Any]:
    session_record = await get_session_or_raise(session, session_id)
    session_record.status = status
    if status != "running" and session_record.completed_at is None:
        session_record.completed_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(session_record)
    logger.info("已更新会话状态 session_id={} status={}", session_id, status)
    return session_to_payload(session_record)


async def list_sessions(session: AsyncSession, card_id: str) -> list[dict[str, Any]]:
    from backend.app.services.card_query_service import get_card_or_raise

    await get_card_or_raise(session, card_id)
    result = await session.execute(
        select(SessionRecord).where(SessionRecord.card_id == card_id).order_by(SessionRecord.created_at.desc())
    )
    sessions = [session_to_payload(item) for item in result.scalars().all()]
    logger.debug("已列出会话 card_id={} count={}", card_id, len(sessions))
    return sessions
