from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from typing import Any

from backend.app.runtime.claude_executor import ClaudeExecutor
from backend.app.runtime.claude_protocol_adapter import ClaudeProtocolAdapter
from common.core.logger import logger


# 执行管理器负责维护运行中进程，并统一封装启动、流式读取、等待与中断语义。
@dataclass(slots=True)
class ExecutionManager:
    executor: ClaudeExecutor = field(default_factory=ClaudeExecutor)
    adapter: ClaudeProtocolAdapter = field(default_factory=ClaudeProtocolAdapter)
    interrupts: set[str] = field(default_factory=set)
    active_processes: dict[str, Any] = field(default_factory=dict)

    async def start(self, execution_id: str, prompt: str) -> dict[str, Any]:
        logger.info("执行管理器开始执行 execution_id={} prompt_length={}", execution_id, len(prompt))
        request = await self.executor.start_process(prompt)
        self.active_processes[execution_id] = request["process"]
        logger.info(
            "执行管理器已启动 execution_id={} pid={} status=running",
            execution_id,
            request["pid"],
        )
        return {
            "execution_id": execution_id,
            "status": "running",
            "command": request["command"],
            "chunks": request["chunks"],
            "mode": request["mode"],
            "pid": request["pid"],
        }

    async def collect(self, execution_id: str) -> list[dict[str, Any]]:
        process = self.active_processes.get(execution_id)
        logger.info("执行管理器开始收集输出 execution_id={} pid={}", execution_id, getattr(process, "pid", None))
        chunks = await self.executor.collect_stream_once(process)
        logger.info("执行管理器完成输出收集 execution_id={} chunk_count={}", execution_id, len(chunks))
        return chunks

    async def stream(self, execution_id: str):
        process = self.active_processes.get(execution_id)
        logger.info("执行管理器开始流式读取 execution_id={} pid={}", execution_id, getattr(process, "pid", None))
        async for chunk in self.executor.stream_process(process):
            yield chunk
        logger.info("执行管理器流式读取结束 execution_id={}", execution_id)

    async def wait(self, execution_id: str) -> dict[str, Any]:
        process = self.active_processes.get(execution_id)
        if process is None:
            logger.warning("等待执行结果时未找到运行中的进程 execution_id={}", execution_id)
            return {"execution_id": execution_id, "status": "missing", "exit_code": None}
        exit_code = await self.executor._wait_process(process)
        status = "finished" if exit_code == 0 and execution_id not in self.interrupts else "stopped"
        if exit_code not in (None, 0) and execution_id not in self.interrupts:
            status = "failed"
        self.active_processes.pop(execution_id, None)
        if execution_id in self.interrupts and status != "stopped":
            self.interrupts.discard(execution_id)
        logger.info(
            "执行管理器等待结束 execution_id={} pid={} status={} exit_code={}",
            execution_id,
            getattr(process, "pid", None),
            status,
            exit_code,
        )
        return {
            "execution_id": execution_id,
            "status": status,
            "exit_code": exit_code,
        }

    async def interrupt(self, execution_id: str) -> dict[str, Any]:
        self.interrupts.add(execution_id)
        process = self.active_processes.get(execution_id)
        logger.warning("执行管理器请求中断 execution_id={} pid={}", execution_id, getattr(process, "pid", None))
        await self.executor.terminate_process(process)
        self.active_processes.pop(execution_id, None)
        return self.adapter.interrupt_payload(execution_id)

    async def fail(self, execution_id: str, error: str) -> dict[str, Any]:
        process = self.active_processes.get(execution_id)
        logger.error(
            "执行管理器标记失败 execution_id={} pid={} error={}",
            execution_id,
            getattr(process, "pid", None),
            error,
        )
        await self.executor.terminate_process(process)
        self.active_processes.pop(execution_id, None)
        return {
            "execution_id": execution_id,
            "status": "failed",
            "error": error,
        }

    def is_interrupted(self, execution_id: str) -> bool:
        interrupted = execution_id in self.interrupts
        logger.debug("执行管理器检查中断状态 execution_id={} interrupted={}", execution_id, interrupted)
        return interrupted

    async def close_all(self) -> None:
        logger.warning("执行管理器准备关闭全部进程 active_count={}", len(self.active_processes))
        for execution_id, process in list(self.active_processes.items()):
            with contextlib.suppress(Exception):
                await self.executor.terminate_process(process)
            self.active_processes.pop(execution_id, None)
            logger.info("执行管理器已关闭进程 execution_id={} pid={}", execution_id, getattr(process, "pid", None))
        self.interrupts.clear()
