from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.file_watch_service import poll_stage_files
from backend.app.services.worktree_service import list_worktree_changed_files
from common.core.exceptions import NotFoundError


async def list_changed_files(session: AsyncSession, card_id: str) -> list[dict[str, Any]]:
    card = await get_card_or_raise(session, card_id)
    worktree_files = await list_worktree_changed_files(session, card_id)
    if worktree_files:
        return worktree_files
    files = await poll_stage_files(session, card_id)
    return files["files"]


async def get_single_file_diff(session: AsyncSession, card_id: str, file_path: str) -> dict[str, Any]:
    await get_card_or_raise(session, card_id)
    path = Path(file_path)
    if not path.is_absolute():
        path = Path(file_path)
    if not path.exists():
        raise NotFoundError(f"Diff target not found: {path}")
    text = path.read_text(encoding="utf-8-sig" if path.suffix == ".csv" else "utf-8")
    lines = text.splitlines()
    diff = "\n".join(f"+ {line}" for line in lines[:50])
    return {
        "path": str(path),
        "diff": diff,
        "line_count": len(lines),
        "summary": f"{path.name} changed with {len(lines)} lines",
    }
