from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from common.core.config import get_settings
from common.core.logger import logger

STREAM_JSON_FLAGS = ["--output-format", "stream-json", "--verbose"]
PROMPT_PREVIEW_LIMIT = 160


# Claude 协议适配器负责拼装 CLI 命令，并把 stream-json 输出标准化为内部事件。
class ClaudeProtocolAdapter:
    def __init__(self) -> None:
        self.settings = get_settings()

    def build_execute_command(self, prompt: str) -> list[str]:
        command = [self.settings.CLAUDE_COMMAND, "-p"]
        if prompt:
            command.append(prompt)
        command.extend(STREAM_JSON_FLAGS)
        logger.debug(
            "已构建 Claude 执行命令 command_preview={} prompt_length={} prompt_preview={}",
            command[:2] + [f"<prompt:{len(prompt)} chars>"] + STREAM_JSON_FLAGS,
            len(prompt),
            prompt[:PROMPT_PREVIEW_LIMIT],
        )
        return command

    def interrupt_payload(self, execution_id: str) -> dict[str, Any]:
        return {
            "type": "control_request",
            "request_id": execution_id,
            "request": {
                "subtype": "interrupt",
            },
        }

    def normalize_stream_chunk(self, chunk: str) -> dict[str, Any]:
        raw_text = chunk.strip()
        if not raw_text:
            logger.debug("收到空的 stream chunk")
            return {"event_type": "raw", "raw_text": "", "payload": None}

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.warning(
                "stream chunk 解析 JSON 失败，降级为原始文本 raw_length={} raw_preview={}",
                len(raw_text),
                raw_text[:PROMPT_PREVIEW_LIMIT],
            )
            return {"event_type": "raw", "raw_text": raw_text, "payload": None}

        event_type = parsed.get("type") or parsed.get("subtype") or "raw"
        logger.debug("已标准化 stream chunk event_type={} raw_length={}", event_type, len(raw_text))
        return {
            "event_type": event_type,
            "raw_text": raw_text,
            "payload": parsed,
        }

    def normalize_many(self, chunks: Iterable[str]) -> list[dict[str, Any]]:
        normalized = [self.normalize_stream_chunk(chunk) for chunk in chunks]
        logger.debug("已标准化 stream chunk 批次 count={}", len(normalized))
        return normalized
