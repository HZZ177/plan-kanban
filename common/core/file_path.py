from __future__ import annotations

from pathlib import Path

from common.core.config import get_settings


def get_project_root() -> Path:
    return get_settings().project_root


def resolve_project_path(relative_path: str) -> Path:
    path = Path(relative_path)
    if path.is_absolute():
        return path
    return get_project_root() / path


def ensure_parent_directory(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
