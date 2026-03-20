from __future__ import annotations

from typing import Any


VALID_EVENT_TYPES = {
    "conversation.delta",
    "process.updated",
    "issues.updated",
    "files.updated",
    "kanban.updated",
    "patch.batch",
    "history.snapshot",
}


def build_ws_event(event_type: str, channel: str, payload: dict[str, Any]) -> dict[str, Any]:
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(f"Unsupported event type: {event_type}")
    return {
        "type": event_type,
        "channel": channel,
        "payload": payload,
    }
