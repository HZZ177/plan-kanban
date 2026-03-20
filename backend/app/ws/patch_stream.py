from __future__ import annotations

from typing import Any

from backend.app.ws.event_schema import build_ws_event


def batch_patch_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    return build_ws_event("patch.batch", "patch", {"events": events, "count": len(events)})
