from __future__ import annotations

from pathlib import Path

from common.core.file_path import ensure_parent_directory, resolve_project_path


def read_text(relative_path: str, encoding: str = "utf-8") -> str:
    return resolve_project_path(relative_path).read_text(encoding=encoding)


def write_text(relative_path: str, content: str, encoding: str = "utf-8") -> Path:
    path = ensure_parent_directory(resolve_project_path(relative_path))
    path.write_text(content, encoding=encoding)
    return path
