from __future__ import annotations

from pathlib import Path

from common.models.card import Card


def build_plan_prompt(card: Card, requirements_path: str | None = None) -> str:
    requirements_line = requirements_path or ""
    return "\n".join(
        [
            "请基于当前卡片生成 Plan 与 Issues CSV。",
            f"card_id: {card.id}",
            f"title: {card.title}",
            f"current_stage: {card.current_stage}",
            f"requirements_path: {requirements_line}",
            f"project_root: {Path(__file__).resolve().parents[3]}",
            "要求：Plan 是合同正文，CSV 由 Plan 的 Issue Contract 直接映射生成。",
        ]
    )
