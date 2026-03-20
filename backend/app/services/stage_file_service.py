from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from common.core.config import get_settings
from common.core.exceptions import NotFoundError

DEFAULT_STAGE_SUPPORT_FILES = {
    "raw": ["docs/Plan-Kanban-需求与架构设计文档.md"],
    "plan": ["docs/Plan-Kanban-需求与架构设计文档.md"],
    "contract": [],
    "developing": [".dev/test/test_plan-kanban-full-platform.py"],
    "acceptance": [".dev/test/test_plan-kanban-full-platform.py"],
}


def _resolve_path(entry: str | Path) -> Path:
    path = Path(entry)
    if path.is_absolute():
        return path
    return get_settings().project_root / path


def _file_payload(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "name": path.name,
        "exists": path.exists(),
    }


def _dedupe_entries(entries: list[Path]) -> list[Path]:
    unique_entries: list[Path] = []
    seen: set[str] = set()
    for entry in entries:
        key = str(entry)
        if key in seen:
            continue
        seen.add(key)
        unique_entries.append(entry)
    return unique_entries


def _build_stage_entries(card) -> list[Path]:
    entries: list[Path] = []

    if card.current_stage in {"contract", "developing", "acceptance"} and card.plan_path:
        entries.append(_resolve_path(card.plan_path))
    if card.current_stage in {"contract", "developing", "acceptance"} and card.issues_path:
        entries.append(_resolve_path(card.issues_path))

    for item in DEFAULT_STAGE_SUPPORT_FILES.get(card.current_stage, []):
        entries.append(_resolve_path(item))

    return _dedupe_entries(entries)


async def list_stage_files(session: AsyncSession, card_id: str) -> list[dict[str, Any]]:
    card = await get_card_or_raise(session, card_id)
    return [_file_payload(path) for path in _build_stage_entries(card)]


async def read_stage_file(session: AsyncSession, card_id: str, file_path: str) -> dict[str, Any]:
    await get_card_or_raise(session, card_id)
    path = _resolve_path(file_path)
    if not path.exists():
        raise NotFoundError(f"Stage file not found: {path}")
    return {
        "path": str(path),
        "name": path.name,
        "content": path.read_text(encoding="utf-8-sig" if path.suffix == ".csv" else "utf-8"),
    }
