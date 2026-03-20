from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.card_query_service import get_card_or_raise
from common.core.exceptions import ValidationError


async def run_plan_precheck(session: AsyncSession, card_id: str) -> dict[str, str | None]:
    card = await get_card_or_raise(session, card_id)
    if card.current_stage != "plan":
        raise ValidationError("generate-contract 只能在 plan 阶段触发")
    project_root = Path(__file__).resolve().parents[3]
    requirements_path = project_root / "docs" / "Plan-Kanban-需求与架构设计文档.md"
    if not requirements_path.exists():
        raise ValidationError(f"Requirements file not found: {requirements_path}")
    return {
        "card_id": card.id,
        "requirements_path": str(requirements_path),
        "current_stage": card.current_stage,
        "title": card.title,
    }
