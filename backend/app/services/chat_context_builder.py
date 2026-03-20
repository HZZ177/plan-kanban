from __future__ import annotations

from typing import Any

from common.core.exceptions import ValidationError
from common.models.card import Card

STAGE_FILE_HINTS = {
    "raw": ["requirement.md", "clarification.md", "notes.md", "references.md"],
    "plan": ["solution.md", "architecture-notes.md", "risks.md", "scope.md"],
    "acceptance": ["review-summary.md", "diff-summary.md", "test-summary.md", "feedback.md"],
}

STAGE_LABELS = {
    "raw": "原始需求澄清",
    "plan": "方案生成",
    "acceptance": "待验收",
}

STAGE_WORKSPACE_FOCUS = {
    "raw": "左侧聚焦需求来源与澄清清单，右侧聚焦追问与总结。",
    "plan": "左侧聚焦方案文档与风险边界，右侧聚焦方案讨论与收敛。",
    "acceptance": "左侧聚焦结果摘要与测试输出，右侧聚焦验收说明与打回意见。",
}


def build_chat_context(card: Card) -> dict[str, Any]:
    if card.current_stage not in STAGE_FILE_HINTS:
        raise ValidationError("Conversation chat is only supported in raw, plan, and acceptance stages")

    return {
        "card_id": card.id,
        "stage_key": card.current_stage,
        "stage_label": STAGE_LABELS[card.current_stage],
        "title": card.title,
        "raw_requirement": card.raw_requirement,
        "plan_path": card.plan_path,
        "issues_path": card.issues_path,
        "file_hints": STAGE_FILE_HINTS[card.current_stage],
        "workspace_focus": STAGE_WORKSPACE_FOCUS[card.current_stage],
    }
