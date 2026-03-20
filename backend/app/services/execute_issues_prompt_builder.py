from __future__ import annotations

from common.models.card import Card


def build_execute_issues_prompt(card: Card, plan_path: str, issues_path: str) -> str:
    return "\n".join(
        [
            "请执行 execute-issues 过程。",
            f"card_id: {card.id}",
            f"title: {card.title}",
            f"plan_path: {plan_path}",
            f"issues_path: {issues_path}",
            "要求：CSV 是唯一状态源，完成后自动进入 acceptance。",
        ]
    )
