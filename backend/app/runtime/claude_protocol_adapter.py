from __future__ import annotations

from collections.abc import Iterable
from typing import Any


class ClaudeProtocolAdapter:
    def build_execute_command(self, prompt: str) -> list[str]:
        return ["claude", "--print", prompt]

    def interrupt_payload(self, execution_id: str) -> dict[str, Any]:
        return {"execution_id": execution_id, "action": "interrupt"}

    def normalize_stream_chunk(self, chunk: str) -> dict[str, Any]:
        return {"event_type": "raw", "raw_text": chunk}

    def normalize_many(self, chunks: Iterable[str]) -> list[dict[str, Any]]:
        return [self.normalize_stream_chunk(chunk) for chunk in chunks]
