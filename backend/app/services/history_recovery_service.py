from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.execution_log_service import list_execution_logs
from backend.app.services.issues_projection_service import sync_issue_states
from backend.app.services.session_history_service import list_session_entries


async def build_history_snapshot(
    session: AsyncSession,
    session_id: str,
    execution_process_id: str | None = None,
    issues_path: str | None = None,
) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "entries": await list_session_entries(session, session_id),
        "logs": [],
        "issues": None,
    }
    if execution_process_id is not None:
        snapshot["logs"] = await list_execution_logs(session, execution_process_id)
    if issues_path is not None:
        snapshot["issues"] = sync_issue_states(issues_path)
    return snapshot
