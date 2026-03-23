from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.event_publish_service import publish_channel_event
from backend.app.services.stage_file_service import list_stage_files
from backend.app.ws.event_schema import build_ws_event
from common.core.logger import logger
from common.core.request_context import set_request_context


# 文件观察服务负责汇总当前阶段文件状态，并向 files 频道广播变化摘要。
async def poll_stage_files(session: AsyncSession, card_id: str) -> dict[str, Any]:
    files = await list_stage_files(session, card_id)
    enriched = [
        {
            **item,
            "modified": Path(item["path"]).stat().st_mtime if Path(item["path"]).exists() else None,
        }
        for item in files
    ]
    payload = {
        "count": len(enriched),
        "files": enriched,
        "updated": [item["path"] for item in enriched if item["exists"]],
    }
    set_request_context(card_id=card_id, channel="files")
    logger.info("已轮询阶段文件 card_id={} count={} updated_count={}", card_id, len(enriched), len(payload["updated"]))
    await publish_channel_event("files", build_ws_event("files.updated", "files", {"card_id": card_id, **payload}))
    return payload
