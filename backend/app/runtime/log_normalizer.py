from __future__ import annotations

from typing import Any


def normalize_log_event(event: dict[str, Any]) -> dict[str, Any]:
    event_type = event.get("event_type", "raw")
    raw_text = event.get("raw_text") or event.get("content") or ""
    entry_type = {
        "raw": "assistant_text",
        "stdout": "assistant_text",
        "stderr": "error",
        "summary": "summary",
    }.get(event_type, "assistant_text")
    role = "assistant" if entry_type != "error" else "assistant"
    return {
        "entry_type": entry_type,
        "role": role,
        "content": raw_text,
        "payload": event.get("payload"),
    }
