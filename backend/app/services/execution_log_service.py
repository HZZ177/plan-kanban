from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from common.core.exceptions import NotFoundError
from common.core.logger import logger
from common.models.execution_process import ExecutionProcess
from common.models.execution_process_log import ExecutionProcessLog


def execution_log_to_payload(log: ExecutionProcessLog) -> dict[str, Any]:
    return {
        "id": log.id,
        "execution_process_id": log.execution_process_id,
        "sequence": log.sequence,
        "stream": log.stream,
        "event_type": log.event_type,
        "payload": log.payload,
        "raw_text": log.raw_text,
    }


# 执行日志服务负责把 runtime 输出按顺序持久化，供恢复与历史查看使用。
async def write_execution_log(
    session: AsyncSession,
    execution_process_id: str,
    stream: str,
    event_type: str,
    raw_text: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    process = await session.get(ExecutionProcess, execution_process_id)
    if process is None:
        logger.warning("写入执行日志时未找到执行进程 execution_process_id={}", execution_process_id)
        raise NotFoundError(f"Execution process not found: {execution_process_id}")
    next_sequence = await session.scalar(
        select(func.coalesce(func.max(ExecutionProcessLog.sequence), 0) + 1).where(
            ExecutionProcessLog.execution_process_id == execution_process_id
        )
    )
    log = ExecutionProcessLog(
        execution_process_id=execution_process_id,
        sequence=int(next_sequence or 1),
        stream=stream,
        event_type=event_type,
        raw_text=raw_text,
        payload=payload,
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    logger.debug(
        "已持久化执行日志 execution_process_id={} sequence={} stream={} event_type={}",
        execution_process_id,
        log.sequence,
        stream,
        event_type,
    )
    return execution_log_to_payload(log)


async def list_execution_logs(session: AsyncSession, execution_process_id: str) -> list[dict[str, Any]]:
    process = await session.get(ExecutionProcess, execution_process_id)
    if process is None:
        logger.warning("查询执行日志时未找到执行进程 execution_process_id={}", execution_process_id)
        raise NotFoundError(f"Execution process not found: {execution_process_id}")
    result = await session.execute(
        select(ExecutionProcessLog)
        .where(ExecutionProcessLog.execution_process_id == execution_process_id)
        .order_by(ExecutionProcessLog.sequence.asc(), ExecutionProcessLog.created_at.asc(), ExecutionProcessLog.id.asc())
    )
    logs = [execution_log_to_payload(item) for item in result.scalars().all()]
    logger.debug("已列出执行日志 execution_process_id={} count={}", execution_process_id, len(logs))
    return logs
