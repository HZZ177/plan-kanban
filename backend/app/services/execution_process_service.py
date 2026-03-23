from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from common.core.exceptions import NotFoundError, ValidationError
from common.core.logger import logger
from common.models.execution_process import ExecutionProcess
from common.models.session import SessionRecord

ALLOWED_EXECUTION_STATUS = {"running", "finished", "failed", "stopped", "aborted"}


def execution_process_to_payload(process: ExecutionProcess) -> dict[str, Any]:
    return {
        "id": process.id,
        "session_id": process.session_id,
        "run_reason": process.run_reason,
        "executor_action": process.executor_action,
        "status": process.status,
        "exit_code": process.exit_code,
        "dropped": process.dropped,
        "pid": process.pid,
        "last_error": process.last_error,
        "started_at": process.started_at.isoformat() if process.started_at else None,
        "completed_at": process.completed_at.isoformat() if process.completed_at else None,
    }


# 执行进程服务负责落库保存运行实例，并维护其状态流转。
async def get_execution_process_or_raise(session: AsyncSession, execution_id: str) -> ExecutionProcess:
    process = await session.get(ExecutionProcess, execution_id)
    if process is None:
        logger.warning("未找到执行进程 execution_process_id={}", execution_id)
        raise NotFoundError(f"Execution process not found: {execution_id}")
    return process


async def create_execution_process(
    session: AsyncSession,
    session_id: str,
    run_reason: str,
    executor_action: dict[str, Any] | None = None,
    pid: int | None = None,
) -> dict[str, Any]:
    session_record = await session.get(SessionRecord, session_id)
    if session_record is None:
        logger.warning("创建执行进程时未找到会话 session_id={}", session_id)
        raise NotFoundError(f"Session not found: {session_id}")
    process = ExecutionProcess(
        session_id=session_id,
        run_reason=run_reason,
        executor_action=executor_action,
        status="running",
        pid=pid,
        started_at=datetime.now(timezone.utc),
    )
    session.add(process)
    await session.commit()
    await session.refresh(process)
    logger.info(
        "已创建执行进程 execution_process_id={} session_id={} run_reason={} pid={}",
        process.id,
        session_id,
        run_reason,
        pid,
    )
    return execution_process_to_payload(process)


async def update_execution_process_status(
    session: AsyncSession,
    execution_id: str,
    status: str,
    exit_code: int | None = None,
    last_error: str | None = None,
    dropped: bool | None = None,
) -> dict[str, Any]:
    if status not in ALLOWED_EXECUTION_STATUS:
        raise ValidationError(f"Unsupported execution status: {status}")
    process = await get_execution_process_or_raise(session, execution_id)
    process.status = status
    process.exit_code = exit_code
    if last_error is not None:
        process.last_error = last_error
    if dropped is not None:
        process.dropped = dropped
    if status != "running":
        process.completed_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(process)
    logger.info(
        "已更新执行进程状态 execution_process_id={} status={} exit_code={} dropped={}",
        execution_id,
        status,
        exit_code,
        process.dropped,
    )
    if last_error:
        logger.warning(
            "执行进程记录错误 execution_process_id={} status={} error={}",
            execution_id,
            status,
            last_error,
        )
    return execution_process_to_payload(process)


async def list_execution_processes(session: AsyncSession, session_id: str | None = None) -> list[dict[str, Any]]:
    stmt = select(ExecutionProcess).order_by(ExecutionProcess.created_at.desc())
    if session_id is not None:
        stmt = stmt.where(ExecutionProcess.session_id == session_id)
    result = await session.execute(stmt)
    processes = [execution_process_to_payload(item) for item in result.scalars().all()]
    logger.debug("已列出执行进程 session_id={} count={}", session_id, len(processes))
    return processes
