from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.app.services.issues_projection_service import sync_issue_states


def summarize_execute_runtime(issues_path: str | Path) -> dict[str, Any]:
    summary = sync_issue_states(issues_path)
    return {
        "issues_path": str(issues_path),
        "total": summary["total"],
        "completed": summary["completed"],
        "failed": summary["failed"],
        "blocked": summary["blocked"],
    }
