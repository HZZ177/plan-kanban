from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.worktree_service import create_worktree, restore_worktree
from common.core.config import get_settings
from common.core.exceptions import ValidationError


def _resolve_project_path(project_id: str) -> Path:
    candidate = get_settings().project_root.parent / project_id
    return candidate if candidate.exists() else get_settings().project_root


async def run_execute_precheck(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    if card.current_stage != "contract":
        raise ValidationError("start-development 只能在 contract 阶段触发")
    if card.active_process_status == "running":
        raise ValidationError("当前卡片已有运行中的 process")
    if not card.plan_path or not Path(card.plan_path).exists():
        raise ValidationError("Plan file not found for current card")
    if not card.issues_path or not Path(card.issues_path).exists():
        raise ValidationError("Issues CSV not found for current card")

    requirements_path: str | None = None
    for line in Path(card.plan_path).read_text(encoding="utf-8").splitlines():
        if line.startswith("requirements_path:"):
            requirements_path = line.split(":", 1)[1].strip()
            break
    if not requirements_path:
        raise ValidationError("Plan frontmatter missing requirements_path")

    requirement_file = Path(requirements_path)
    if not requirement_file.is_absolute():
        requirement_file = get_settings().project_root / requirement_file
    if not requirement_file.exists():
        raise ValidationError(f"Requirements file not found: {requirement_file}")

    worktree = await restore_worktree(session, card_id) if card.worktree_path else await create_worktree(session, card_id)
    project_path = _resolve_project_path(card.project_id)
    test_path = get_settings().project_root / ".dev" / "test" / f"test_{Path(card.issues_path).stem}.py"
    return {
        "card": {
            "id": card.id,
            "project_id": card.project_id,
            "title": card.title,
            "current_stage": card.current_stage,
            "plan_path": card.plan_path,
            "issues_path": card.issues_path,
            "worktree_path": worktree["worktree_path"],
            "branch_name": worktree["branch_name"],
        },
        "project_root": str(get_settings().project_root),
        "project_path": str(project_path),
        "plan_path": card.plan_path,
        "issues_path": card.issues_path,
        "requirements_path": str(requirement_file),
        "worktree": worktree,
        "output_paths": {
            "test_path": str(test_path),
        },
    }
