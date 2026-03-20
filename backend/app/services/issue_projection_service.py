from __future__ import annotations

from typing import Any


def build_issue_rows(issues: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for issue in issues:
        refs = issue.get("refs")
        if not refs:
            design_refs = issue.get("design_refs", [])
            code_refs = issue.get("code_refs", [])
            refs = "; ".join([*design_refs, *code_refs])
        rows.append(
            {
                "id": issue["id"],
                "priority": issue["priority"],
                "title": issue["title"],
                "refs": refs,
                "dev_state": issue.get("dev_state", "未开始"),
                "test_state": issue.get("test_state", "未开始"),
                "owner": issue.get("owner", ""),
                "notes": issue.get("notes", ""),
            }
        )
    return rows
