from __future__ import annotations

from typing import Any

from backend.app.ws.event_bus import GLOBAL_EVENT_BUS
from backend.app.ws.patch_stream import batch_patch_events
from common.core.logger import logger
from common.core.request_context import get_request_context


# 事件发布服务负责为事件补齐链路上下文，并同时向业务频道与 patch 频道广播。
def _inject_event_context(event: dict[str, Any]) -> dict[str, Any]:
    context = get_request_context()
    payload = dict(event.get("payload") or {})
    payload.setdefault("trace_id", context.get("trace_id"))
    payload.setdefault("request_id", context.get("request_id"))
    return {
        **event,
        "payload": payload,
    }


async def publish_channel_event(channel: str, event: dict[str, Any]) -> None:
    contextual_event = _inject_event_context(event)
    logger.info(
        "开始发布频道事件 channel={} event_type={} payload_keys={}",
        channel,
        contextual_event.get("type"),
        sorted((contextual_event.get("payload") or {}).keys()),
    )
    await GLOBAL_EVENT_BUS.publish(channel, contextual_event)
    await GLOBAL_EVENT_BUS.publish("patch", batch_patch_events([contextual_event], channel=channel))
    logger.debug("频道事件发布完成 channel={} event_type={} patch_count=1", channel, contextual_event.get("type"))
