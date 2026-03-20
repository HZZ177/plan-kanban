from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.stage_file_service import list_stage_files
from common.core.config import get_settings
from common.core.exceptions import NotFoundError


async def list_changed_files(session: AsyncSession, card_id: str) -> list[dict[str, Any]]:
    await get_card_or_raise(session, card_id)
    files = await list_stage_files(session, card_id)
    return [item for item in files if item["exists"]]


async def get_single_file_diff(session: AsyncSession, card_id: str, file_path: str) -> dict[str, Any]:
    await get_card_or_raise(session, card_id)
    path = Path(file_path)
    if not path.is_absolute():
        path = get_settings().project_root / path
    if not path.exists():
        raise NotFoundError(f"Diff target not found: {path}")
    text = path.read_text(encoding="utf-8-sig" if path.suffix == ".csv" else "utf-8")
    preview = "\n".join(text.splitlines()[:20])
    return {"path": str(path), "diff": preview, "line_count": len(text.splitlines())}
