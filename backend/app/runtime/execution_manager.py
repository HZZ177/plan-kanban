from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.app.runtime.claude_executor import ClaudeExecutor
from backend.app.runtime.claude_protocol_adapter import ClaudeProtocolAdapter


@dataclass(slots=True)
class ExecutionManager:
    executor: ClaudeExecutor = field(default_factory=ClaudeExecutor)
    adapter: ClaudeProtocolAdapter = field(default_factory=ClaudeProtocolAdapter)
    interrupts: set[str] = field(default_factory=set)

    def start(self, execution_id: str, prompt: str) -> dict[str, Any]:
        preview = self.executor.run_preview(prompt)
        return {
            "execution_id": execution_id,
            "status": "running",
            "command": preview["command"],
            "chunks": preview["chunks"],
        }

    def interrupt(self, execution_id: str) -> dict[str, Any]:
        self.interrupts.add(execution_id)
        return self.adapter.interrupt_payload(execution_id)

    def is_interrupted(self, execution_id: str) -> bool:
        return execution_id in self.interrupts
