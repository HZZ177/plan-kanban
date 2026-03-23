from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.plan_file_service import build_plan_paths
from common.core.config import get_settings
from common.core.exceptions import ValidationError


async def run_plan_precheck(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    if card.current_stage != "plan":
        raise ValidationError("generate-contract 只能在 plan 阶段触发")
    if card.active_process_status == "running":
        raise ValidationError("当前卡片已有运行中的 process")

    settings = get_settings()
    project_root = settings.project_root
    requirements_path = project_root / "docs" / "Plan-Kanban-需求与架构设计文档.md"
    if not requirements_path.exists():
        raise ValidationError(f"Requirements file not found: {requirements_path}")

    plan_path, issues_path, basename = build_plan_paths(card.title)
    test_path = project_root / ".dev" / "test" / f"test_{basename}.py"

    return {
        "card": {
            "id": card.id,
            "project_id": card.project_id,
            "title": card.title,
            "summary": card.summary,
            "owner": card.owner,
            "priority": card.priority,
            "raw_requirement": card.raw_requirement,
            "current_stage": card.current_stage,
            "latest_session_id": card.latest_session_id,
            "active_process_type": card.active_process_type,
            "active_process_status": card.active_process_status,
            "active_process_session_id": card.active_process_session_id,
            "existing_plan_path": card.plan_path,
            "existing_issues_path": card.issues_path,
        },
        "requirements_path": str(requirements_path),
        "project_root": str(project_root),
        "cwd": str(project_root),
        "stage_files": [str(requirements_path)],
        "output_paths": {
            "basename": basename,
            "plan_path": str(plan_path),
            "issues_path": str(issues_path),
            "test_path": str(test_path),
        },
    }
