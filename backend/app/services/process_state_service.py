from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.schemas.process_state import ProcessStateSchema
from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.event_publish_service import publish_channel_event
from backend.app.ws.event_schema import build_ws_event
from common.core.exceptions import ValidationError
from common.core.logger import logger
from common.core.request_context import set_request_context

ALLOWED_PROCESS_TYPES = {"none", "conversation", "skill_plan", "skill_execute_issues"}
ALLOWED_PROCESS_STATUSES = {"idle", "running", "finished", "failed"}


# 进程状态服务负责同步卡片上的当前进程状态，并广播给 process 频道。
async def update_process_state(session: AsyncSession, card_id: str, payload: ProcessStateSchema) -> dict[str, str | None]:
    if payload.active_process_type not in ALLOWED_PROCESS_TYPES:
        raise ValidationError(f"Unsupported process type: {payload.active_process_type}")
    if payload.active_process_status not in ALLOWED_PROCESS_STATUSES:
        raise ValidationError(f"Unsupported process status: {payload.active_process_status}")

    card = await get_card_or_raise(session, card_id)
    card.active_process_type = payload.active_process_type
    card.active_process_status = payload.active_process_status
    card.active_process_session_id = payload.active_process_session_id

    await session.commit()
    await session.refresh(card)
    state = {
        "active_process_type": card.active_process_type,
        "active_process_status": card.active_process_status,
        "active_process_session_id": card.active_process_session_id,
    }
    set_request_context(card_id=card_id, session_id=card.active_process_session_id, channel="process")
    logger.info(
        "已更新进程状态 card_id={} process_type={} process_status={} session_id={}",
        card_id,
        card.active_process_type,
        card.active_process_status,
        card.active_process_session_id,
    )
    await publish_channel_event("process", build_ws_event("process.updated", "process", {"card_id": card_id, **state}))
    return state


async def get_process_state(session: AsyncSession, card_id: str) -> dict[str, str | None]:
    card = await get_card_or_raise(session, card_id)
    state = {
        "active_process_type": card.active_process_type,
        "active_process_status": card.active_process_status,
        "active_process_session_id": card.active_process_session_id,
    }
    logger.debug("已加载进程状态 card_id={} status={}", card_id, card.active_process_status)
    return state
