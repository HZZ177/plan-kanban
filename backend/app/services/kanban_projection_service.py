from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import list_cards

STAGE_ORDER = ["raw", "plan", "contract", "developing", "acceptance"]
STAGE_TITLES = {
    "raw": "原始需求澄清",
    "plan": "方案生成",
    "contract": "澄清&拆解执行合同",
    "developing": "开发中",
    "acceptance": "待验收",
}


async def get_kanban_projection(session: AsyncSession) -> dict[str, list[dict[str, Any]]]:
    cards = await list_cards(session)
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
    return {"stages": stages}
