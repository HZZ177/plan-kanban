from __future__ import annotations

from typing import Any

from backend.app.ws.event_schema import build_ws_event
from common.core.logger import logger


READY_EVENT_TYPES = {
    "conversation": "conversation.delta",
    "process": "process.updated",
    "issues": "issues.updated",
    "files": "files.updated",
    "kanban": "kanban.updated",
}


# patch_stream 负责为前端封装 ready / batch / finished 这类补丁事件结构。
def batch_patch_events(events: list[dict[str, Any]], channel: str = "patch") -> dict[str, Any]:
    logger.debug("开始构建补丁批次事件 channel={} count={}", channel, len(events))
    return build_ws_event(
        "patch.batch",
        channel,
        {
            "events": events,
            "count": len(events),
            "finished": False,
        },
    )


def build_ready_event(channel: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    event_type = READY_EVENT_TYPES[channel]
    logger.debug("开始构建就绪事件 channel={} event_type={}", channel, event_type)
    return build_ws_event(event_type, channel, {"ready": True, **(payload or {})})


def build_finished_event(channel: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    logger.debug("开始构建补丁完成事件 channel={}", channel)
    return build_ws_event(
        "patch.batch",
        channel,
        {
            "events": [],
            "count": 0,
            "finished": True,
            **(payload or {}),
        },
    )
