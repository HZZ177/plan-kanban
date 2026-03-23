from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.execution_log_service import list_execution_logs
from backend.app.services.file_watch_service import poll_stage_files
from backend.app.services.issues_projection_service import sync_issue_states
from backend.app.services.process_state_service import get_process_state
from backend.app.services.session_history_service import list_session_entries
from common.core.exceptions import ValidationError
from common.core.logger import logger


# 恢复服务负责聚合会话历史、执行日志、进程状态与文件快照，供前端恢复工作区使用。
async def build_history_snapshot(
    session: AsyncSession,
    session_id: str,
    execution_process_id: str | None = None,
    issues_path: str | None = None,
    card_id: str | None = None,
) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "entries": await list_session_entries(session, session_id),
        "logs": [],
        "issues": None,
        "process": None,
        "files": None,
    }
    if execution_process_id is not None:
        snapshot["logs"] = await list_execution_logs(session, execution_process_id)
    if issues_path is not None:
        snapshot["issues"] = sync_issue_states(issues_path)
    if card_id is not None:
        snapshot["process"] = await get_process_state(session, card_id)
        snapshot["files"] = await poll_stage_files(session, card_id)
    logger.info(
        "已构建历史快照 session_id={} execution_process_id={} has_issues={} has_process={} has_files={}",
        session_id,
        execution_process_id,
        snapshot["issues"] is not None,
        snapshot["process"] is not None,
        snapshot["files"] is not None,
    )
    return snapshot


async def build_recovery_snapshot(session: AsyncSession, card_id: str, session_id: str) -> dict[str, Any]:
    from backend.app.services.card_query_service import get_card_or_raise
    from backend.app.services.execution_process_service import list_execution_processes

    card = await get_card_or_raise(session, card_id)
    if card.active_process_session_id and card.active_process_session_id != session_id:
        logger.warning(
            "恢复快照会话不匹配 card_id={} active_session_id={} request_session_id={}",
            card_id,
            card.active_process_session_id,
            session_id,
        )
        raise ValidationError("Session does not match card active process session")
    processes = await list_execution_processes(session, session_id=session_id)
    execution_process_id = processes[0]["id"] if processes else None
    logger.info(
        "开始构建恢复快照 card_id={} session_id={} execution_process_id={}",
        card_id,
        session_id,
        execution_process_id,
    )
    return await build_history_snapshot(
        session,
        session_id,
        execution_process_id=execution_process_id,
        issues_path=card.issues_path,
        card_id=card_id,
    )
