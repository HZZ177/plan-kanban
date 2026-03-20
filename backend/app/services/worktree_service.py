from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from common.core.config import get_settings
from common.core.exceptions import ValidationError


def _worktree_base(card_id: str) -> Path:
    return get_settings().project_root / ".claude" / "worktrees" / card_id


async def create_worktree(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    path = _worktree_base(card_id)
    path.mkdir(parents=True, exist_ok=True)
    card.worktree_path = str(path)
    card.branch_name = f"worktree/{card_id}"
    await session.commit()
    await session.refresh(card)
    return {"worktree_path": card.worktree_path, "branch_name": card.branch_name}


async def restore_worktree(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    if not card.worktree_path:
        raise ValidationError("Worktree has not been created")
    path = Path(card.worktree_path)
    path.mkdir(parents=True, exist_ok=True)
    return {"worktree_path": str(path), "exists": path.exists(), "branch_name": card.branch_name}


async def cleanup_worktree(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    if not card.worktree_path:
        return {"removed": False, "worktree_path": None}
    path = Path(card.worktree_path)
    if path.exists() and path.is_dir():
        for child in path.iterdir():
            if child.is_file():
                child.unlink()
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
    return {"status": "healthy" if path.exists() else "missing", "worktree_path": str(path)}
