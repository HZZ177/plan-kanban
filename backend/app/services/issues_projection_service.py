from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from common.core.exceptions import ValidationError


REQUIRED_HEADERS = ["id", "priority", "title", "refs", "dev_state", "test_state", "owner", "notes"]


def read_issue_projection(csv_path: str | Path) -> list[dict[str, str]]:
    path = Path(csv_path)
    if not path.exists():
        raise ValidationError(f"Issues CSV not found: {path}")
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if list(headers) != REQUIRED_HEADERS:
            raise ValidationError("Issues CSV headers are invalid")
        return [dict(row) for row in reader]


def sync_issue_states(csv_path: str | Path) -> dict[str, Any]:
    rows = read_issue_projection(csv_path)
    total = len(rows)
    completed = sum(1 for row in rows if row["dev_state"] == "已完成" and row["test_state"] == "已完成")
    failed = sum(1 for row in rows if row["test_state"] == "失败")
    blocked = sum(1 for row in rows if row["dev_state"] == "进行中" and "blocked:" in (row.get("notes") or ""))
    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "blocked": blocked,
        "rows": rows,
    }
