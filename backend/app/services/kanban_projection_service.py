from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import list_cards
from backend.app.services.event_publish_service import publish_channel_event
from backend.app.ws.event_schema import build_ws_event
from common.core.logger import logger
from common.core.request_context import set_request_context

STAGE_ORDER = ["raw", "plan", "contract", "developing", "acceptance"]
STAGE_TITLES = {
    "raw": "原始需求澄清",
    "plan": "方案生成",
    "contract": "澄清&拆解执行合同",
    "developing": "开发中",
    "acceptance": "待验收",
}


async def get_kanban_projection(session: AsyncSession, project_id: str | None = None) -> dict[str, list[dict[str, Any]]]:
    cards = await list_cards(session, project_id=project_id)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for card in cards:
        grouped[card["current_stage"]].append(card)

    stages = [
        {
            "key": stage,
            "title": STAGE_TITLES.get(stage, stage),
            "count": len(grouped[stage]),
            "items": grouped[stage],
        }
        for stage in STAGE_ORDER
    ]
    payload = {"stages": stages, "project_id": project_id}
    set_request_context(channel="kanban")
    logger.info("Built kanban projection project_id={} stage_count={} card_count={}", project_id, len(stages), len(cards))
    await publish_channel_event("kanban", build_ws_event("kanban.updated", "kanban", payload))
    return payload
