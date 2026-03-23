from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.services.acceptance_substate_service import update_acceptance_substate
from backend.app.services.card_query_service import get_card_or_raise
from backend.app.services.card_transition_service import advance_card_to_developing
from backend.app.services.diff_service import get_single_file_diff, list_changed_files
from backend.app.services.issue_runtime_service import summarize_execute_runtime
from common.core.logger import logger


# 验收服务负责整理验收摘要，并在需要时把卡片从验收阶段回退到开发阶段。
async def build_acceptance_summary(session: AsyncSession, card_id: str) -> dict[str, Any]:
    card = await get_card_or_raise(session, card_id)
    changed_files = await list_changed_files(session, card_id)
    preview = None
    preview_path = card.issues_path or (changed_files[0]["path"] if changed_files else None)
    if preview_path:
        preview = await get_single_file_diff(session, card_id, preview_path)
    runtime = summarize_execute_runtime(card.issues_path) if card.issues_path else None
    summary = {
        "card_id": card.id,
        "current_stage": card.current_stage,
        "changed_files": changed_files,
        "preview": preview,
        "acceptance_substate": card.acceptance_substate,
        "runtime": runtime,
        "can_rollback": card.current_stage == "acceptance",
    }
    logger.info(
        "已构建验收摘要 card_id={} stage={} changed_files={} can_rollback={}",
        card_id,
        card.current_stage,
        len(changed_files),
        summary["can_rollback"],
    )
    return summary


async def rollback_acceptance(session: AsyncSession, card_id: str) -> dict[str, Any]:
    logger.warning("准备回退验收状态 card_id={}", card_id)
    await update_acceptance_substate(session, card_id, "已打回")
    result = await advance_card_to_developing(session, card_id)
    logger.info("验收已回退到开发阶段 card_id={} next_stage={}", card_id, result.get("current_stage"))
    return result
