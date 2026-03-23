from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.issues_projection_service import read_issue_projection
from common.core.config import get_settings
from common.core.exceptions import ValidationError
from common.models.issue_index import IssueIndex


def _worktree_base(card_id: str) -> Path:
    return get_settings().project_root / ".claude" / "worktrees" / card_id


def _project_repo_path(card) -> Path:
    candidate = get_settings().project_root.parent / card.project_id
    return candidate if candidate.exists() else get_settings().project_root


async def create_worktree(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    repo_path = _project_repo_path(card)
    path = _worktree_base(card_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.mkdir(parents=True, exist_ok=True)
    git_dir = path / ".git"
    if not git_dir.exists():
        git_dir.write_text(f"gitdir: {repo_path}\n", encoding="utf-8")
    card.worktree_path = str(path)
    card.branch_name = f"worktree/{card_id}"
    await session.commit()
    await session.refresh(card)
    return {
        "worktree_path": card.worktree_path,
        "branch_name": card.branch_name,
        "repo_path": str(repo_path),
        "exists": path.exists(),
    }


async def restore_worktree(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    if not card.worktree_path:
        raise ValidationError("Worktree has not been created")
    path = Path(card.worktree_path)
    path.mkdir(parents=True, exist_ok=True)
    return {
        "worktree_path": str(path),
        "exists": path.exists(),
        "branch_name": card.branch_name,
        "repo_path": str(_project_repo_path(card)),
    }


async def cleanup_worktree(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    if not card.worktree_path:
        return {"removed": False, "worktree_path": None}
    path = Path(card.worktree_path)
    if path.exists() and path.is_dir():
        for child in list(path.iterdir()):
            if child.is_file():
                child.unlink(missing_ok=True)
        for child in list(path.iterdir()):
            if child.is_dir():
                raise ValidationError("Worktree contains nested directories and cannot be cleaned safely")
        path.rmdir()
    card.worktree_path = None
    card.branch_name = None
    await session.commit()
    await session.refresh(card)
    return {"removed": True, "worktree_path": None}


async def recover_worktree_error(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    if not card.worktree_path:
        return {"status": "noop", "worktree_path": None}
    path = Path(card.worktree_path)
    return {
        "status": "healthy" if path.exists() else "missing",
        "worktree_path": str(path),
        "branch_name": card.branch_name,
    }


async def list_worktree_changed_files(session: AsyncSession, card_id: str) -> list[dict[str, Any]]:
    card = await get_card_or_raise(session, card_id)
    if not card.issues_path:
        return []
    result = await session.execute(
        select(IssueIndex).where(IssueIndex.card_id == card_id).order_by(IssueIndex.sort_order.asc())
    )
    items = result.scalars().all()
    if not items:
        rows = read_issue_projection(card.issues_path)
        return [
            {
                "path": str(Path(card.issues_path)),
                "name": Path(card.issues_path).name,
                "source": "issues_csv",
                "issue_id": row["id"],
                "dev_state": row["dev_state"],
                "test_state": row["test_state"],
                "exists": Path(card.issues_path).exists(),
            }
            for row in rows
        ]
    return [
        {
            "path": str(Path(card.issues_path)),
            "name": Path(card.issues_path).name,
            "source": "issues_csv",
            "issue_id": item.issue_id,
            "dev_state": item.dev_state,
            "test_state": item.test_state,
            "exists": Path(card.issues_path).exists(),
        }
        for item in items
    ]
