from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.core.exceptions import NotFoundError
from common.models.execution_process import ExecutionProcess
from common.models.execution_process_log import ExecutionProcessLog


def execution_log_to_payload(log: ExecutionProcessLog) -> dict[str, Any]:
    return {
        "id": log.id,
        "execution_process_id": log.execution_process_id,
        "stream": log.stream,
        "event_type": log.event_type,
        "payload": log.payload,
        "raw_text": log.raw_text,
    }


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
        raise NotFoundError(f"Execution process not found: {execution_process_id}")
    log = ExecutionProcessLog(
        execution_process_id=execution_process_id,
        stream=stream,
        event_type=event_type,
        raw_text=raw_text,
        payload=payload,
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return execution_log_to_payload(log)


async def list_execution_logs(session: AsyncSession, execution_process_id: str) -> list[dict[str, Any]]:
    process = await session.get(ExecutionProcess, execution_process_id)
    if process is None:
        raise NotFoundError(f"Execution process not found: {execution_process_id}")
    result = await session.execute(
        select(ExecutionProcessLog)
        .where(ExecutionProcessLog.execution_process_id == execution_process_id)
        .order_by(ExecutionProcessLog.created_at.asc(), ExecutionProcessLog.id.asc())
    )
    return [execution_log_to_payload(item) for item in result.scalars().all()]
