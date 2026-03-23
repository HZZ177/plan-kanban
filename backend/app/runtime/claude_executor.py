from __future__ import annotations

import asyncio
import contextlib
import inspect
import subprocess
from asyncio.subprocess import Process
from dataclasses import dataclass, field
from typing import Any

from backend.app.runtime.claude_protocol_adapter import ClaudeProtocolAdapter
from common.core.logger import logger


# Claude 执行器负责启动 Claude CLI 子进程，并把 stdout/stderr 转成可消费的流式事件。
@dataclass(slots=True)
class ClaudeExecutor:
    adapter: ClaudeProtocolAdapter = field(default_factory=ClaudeProtocolAdapter)

    def bootstrap(self) -> dict[str, Any]:
        payload = {
            "executor": "claude",
            "ready": True,
            "supports_interrupt": True,
            "command_preview": self.adapter.build_execute_command("bootstrap"),
            "stream_format": "stream-json",
        }
        logger.info("Claude 执行器已初始化 stream_format={}", payload["stream_format"])
        return payload

    def build_execution_request(self, prompt: str) -> dict[str, Any]:
        command = self.adapter.build_execute_command(prompt)
        request = {
            "command": command,
            "prompt": prompt,
            "chunks": [],
            "mode": "cli-stream",
        }
        logger.debug(
            "已构建执行请求 mode={} prompt_length={} command_size={}",
            request["mode"],
            len(prompt),
            len(command),
        )
        return request

    async def start_process(self, prompt: str) -> dict[str, Any]:
        request = self.build_execution_request(prompt)
        try:
            process = await asyncio.create_subprocess_exec(
                *request["command"],
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            logger.info("通过 asyncio 启动 Claude 子进程成功 pid={}", process.pid)
        except NotImplementedError:
            logger.warning("当前环境不支持 asyncio 子进程，降级使用 subprocess.Popen")
            process = await asyncio.to_thread(
                subprocess.Popen,
                request["command"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info("通过 subprocess.Popen 启动 Claude 子进程成功 pid={}", process.pid)
        except Exception:
            logger.exception("启动 Claude 子进程失败")
            raise
        return {
            **request,
            "process": process,
            "pid": process.pid,
        }

    async def _wait_process(self, process: Process | subprocess.Popen[bytes]) -> int | None:
        wait_fn = getattr(process, "wait")
        if inspect.iscoroutinefunction(wait_fn):
            exit_code = await wait_fn()
        else:
            exit_code = await asyncio.to_thread(wait_fn)
        logger.info("Claude 子进程等待结束 pid={} exit_code={}", process.pid, exit_code)
        return exit_code

    async def terminate_process(self, process: Process | subprocess.Popen[bytes] | None) -> None:
        if process is None:
            logger.debug("跳过终止进程：未找到运行实例")
            return
        if process.returncode is not None:
            logger.debug("跳过终止进程：进程已退出 pid={} exit_code={}", process.pid, process.returncode)
            return
        logger.warning("准备终止 Claude 子进程 pid={}", process.pid)
        process.terminate()
        with contextlib.suppress(ProcessLookupError, OSError, subprocess.TimeoutExpired):
            await asyncio.wait_for(self._wait_process(process), timeout=2)

    async def _read_stream_line(self, stream: Any) -> bytes:
        if stream is None:
            return b""
        readline = getattr(stream, "readline", None)
        if readline is None:
            return b""
        if inspect.iscoroutinefunction(readline):
            return await readline()
        return await asyncio.to_thread(readline)

    async def stream_process(self, process: Process | subprocess.Popen[bytes] | None):
        if process is None:
            logger.warning("跳过流式读取：未找到运行实例")
            return

        logger.info("开始读取子进程输出流 pid={}", process.pid)
        queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
        stream_activity = {"stdout": 0, "stderr": 0}

        async def pump(stream: Any, stream_name: str) -> None:
            if stream is None:
                await queue.put(None)
                return
            try:
                while True:
                    line = await self._read_stream_line(stream)
                    if not line:
                        break
                    raw_chunk = line.decode("utf-8", errors="replace")
                    payload = self.adapter.normalize_stream_chunk(raw_chunk)
                    if stream_name != "stdout":
                        payload["stream"] = stream_name
                    stream_activity[stream_name] += 1
                    logger.debug(
                        "收到子进程输出块 pid={} stream={} event_type={} raw_chunk={} ",
                        process.pid,
                        stream_name,
                        payload.get("event_type"),
                        raw_chunk.rstrip("\r\n"),
                    )
                    await queue.put(payload)
            finally:
                logger.debug(
                    "子进程输出泵结束 pid={} stream={} chunk_count={}",
                    process.pid,
                    stream_name,
                    stream_activity[stream_name],
                )
                await queue.put(None)

        stdout_task = asyncio.create_task(pump(getattr(process, "stdout", None), "stdout"))
        stderr_task = asyncio.create_task(pump(getattr(process, "stderr", None), "stderr"))
        finished_streams = 0
        try:
            while finished_streams < 2:
                item = await queue.get()
                if item is None:
                    finished_streams += 1
                    continue
                yield item
        finally:
            for task in (stdout_task, stderr_task):
                if not task.done():
                    task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await task
            logger.info(
                "子进程输出流读取完成 pid={} stdout_chunks={} stderr_chunks={}",
                process.pid,
                stream_activity["stdout"],
                stream_activity["stderr"],
            )

    async def collect_stream_once(self, process: Process | subprocess.Popen[bytes] | None) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []
        async for chunk in self.stream_process(process):
            chunks.append(chunk)
        logger.info("已完成子进程输出收集 pid={} count={}", getattr(process, "pid", None), len(chunks))
        return chunks
