from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from backend.app.runtime.claude_protocol_adapter import ClaudeProtocolAdapter


@dataclass(slots=True)
class ClaudeExecutor:
    adapter: ClaudeProtocolAdapter = field(default_factory=ClaudeProtocolAdapter)

    def bootstrap(self) -> dict[str, Any]:
        return {
            "executor": "claude",
            "ready": True,
            "supports_interrupt": True,
            "command_preview": self.adapter.build_execute_command("bootstrap"),
        }

    def run_preview(self, prompt: str) -> dict[str, Any]:
        command = self.adapter.build_execute_command(prompt)
        return {
            "command": command,
            "prompt": prompt,
            "chunks": self.adapter.normalize_many([f"preview:{prompt}"]),
        }
