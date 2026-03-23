from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.event_publish_service import publish_channel_event
from backend.app.ws.event_schema import build_ws_event
from common.core.exceptions import ValidationError
from common.core.logger import logger
from common.core.request_context import set_request_context
from common.models.issue_index import IssueIndex

REQUIRED_HEADERS = ["id", "priority", "title", "refs", "dev_state", "test_state", "owner", "notes"]


# Issues 投影视图服务负责读取 CSV 状态源，并同步数据库索引与 issues 频道广播。
def read_issue_projection(csv_path: str | Path) -> list[dict[str, str]]:
    path = Path(csv_path)
    if not path.exists():
        raise ValidationError(f"Issues CSV not found: {path}")
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        if list(headers) != REQUIRED_HEADERS:
            raise ValidationError("Issues CSV headers are invalid")
        rows = [dict(row) for row in reader]
        logger.debug("已读取 issues 投影文件 path={} count={}", path, len(rows))
        return rows


def sync_issue_states(csv_path: str | Path) -> dict[str, Any]:
    rows = read_issue_projection(csv_path)
    total = len(rows)
    completed = sum(1 for row in rows if row["dev_state"] == "已完成" and row["test_state"] == "已完成")
    failed = sum(1 for row in rows if row["test_state"] == "失败")
    blocked = sum(1 for row in rows if row["dev_state"] == "进行中" and "blocked:" in (row.get("notes") or ""))
    running = sum(1 for row in rows if row["dev_state"] == "进行中")
    summary = {
        "total": total,
        "completed": completed,
        "failed": failed,
        "blocked": blocked,
        "running": running,
        "rows": rows,
    }
    logger.info(
        "已同步 issues 状态 path={} total={} completed={} failed={} blocked={} running={}",
        csv_path,
        total,
        completed,
        failed,
        blocked,
        running,
    )
    return summary


async def rebuild_issue_index(session: AsyncSession, card_id: str, csv_path: str | Path) -> list[dict[str, Any]]:
    rows = read_issue_projection(csv_path)
    issue_ids = [row["id"] for row in rows]
    await session.execute(delete(IssueIndex).where(IssueIndex.card_id == card_id))
    if issue_ids:
        await session.execute(delete(IssueIndex).where(IssueIndex.issue_id.in_(issue_ids)))
    entries: list[IssueIndex] = []
    for index, row in enumerate(rows):
        entries.append(
            IssueIndex(
                card_id=card_id,
                issue_id=row["id"],
                priority=row["priority"],
                title=row["title"],
                refs=row["refs"],
                dev_state=row["dev_state"],
                test_state=row["test_state"],
                owner=row.get("owner") or None,
                notes=row.get("notes") or None,
                sort_order=index,
            )
        )
    session.add_all(entries)
    await session.commit()
    payload = [issue_index_to_payload(item) for item in entries]
    set_request_context(card_id=card_id, channel="issues")
    logger.info("已重建 issues 索引 card_id={} count={}", card_id, len(payload))
    await publish_channel_event(
        "issues",
        build_ws_event("issues.updated", "issues", {"card_id": card_id, "items": payload}),
    )
    return payload


async def list_issue_index(session: AsyncSession, card_id: str) -> list[dict[str, Any]]:
    result = await session.execute(
        select(IssueIndex).where(IssueIndex.card_id == card_id).order_by(IssueIndex.sort_order.asc(), IssueIndex.created_at.asc())
    )
    payload = [issue_index_to_payload(item) for item in result.scalars().all()]
    logger.debug("已列出 issues 索引 card_id={} count={}", card_id, len(payload))
    return payload


def issue_index_to_payload(item: IssueIndex) -> dict[str, Any]:
    return {
        "card_id": item.card_id,
        "issue_id": item.issue_id,
        "priority": item.priority,
        "title": item.title,
        "refs": item.refs,
        "dev_state": item.dev_state,
        "test_state": item.test_state,
        "owner": item.owner,
        "notes": item.notes,
        "sort_order": item.sort_order,
    }
