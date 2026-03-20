from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from common.core.config import get_settings


def build_plan_basename(card_title: str, created_at: datetime | None = None) -> str:
    now = created_at or datetime.now(timezone.utc)
    slug = "-".join(card_title.lower().replace("_", " ").split()) or "plan-kanban-task"
    safe_slug = "".join(ch if ch.isalnum() or ch == "-" else "-" for ch in slug).strip("-") or "plan-kanban-task"
    return f"{now.astimezone().strftime('%Y-%m-%d_%H-%M-%S')}-{safe_slug}"


def build_plan_paths(card_title: str, created_at: datetime | None = None) -> tuple[Path, Path, str]:
    settings = get_settings()
    basename = build_plan_basename(card_title, created_at)
    plan_path = settings.project_root / ".dev" / "plans" / f"{basename}.md"
    issues_path = settings.project_root / ".dev" / "issues" / f"{basename}.csv"
    return plan_path, issues_path, basename


def write_plan_file(plan_path: Path, content: str) -> Path:
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    if plan_path.exists():
        raise FileExistsError(f"Plan file already exists: {plan_path}")
    plan_path.write_text(content, encoding="utf-8")
    return plan_path
