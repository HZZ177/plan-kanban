from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from fastapi import WebSocket

from common.core.logger import logger


# 事件总线负责管理 WebSocket 订阅、广播与心跳，保证各频道事件能够统一分发。
@dataclass(slots=True)
class EventBus:
    subscribers: dict[str, set[WebSocket]] = field(default_factory=lambda: defaultdict(set))

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.subscribers[channel].add(websocket)
        logger.info(
            "WebSocket 已连接 channel={} subscriber_count={} client={}",
            channel,
            len(self.subscribers[channel]),
            getattr(websocket.client, "host", None),
        )

    def disconnect(self, channel: str, websocket: WebSocket) -> None:
        subscribers = self.subscribers.get(channel)
        if subscribers is None:
            logger.info(
                "WebSocket 已断开 channel={} subscriber_count=0 client={}",
                channel,
                getattr(websocket.client, "host", None),
            )
            return
        subscribers.discard(websocket)
        remaining = len(subscribers)
        if not subscribers:
            self.subscribers.pop(channel, None)
        logger.info(
            "WebSocket 已断开 channel={} subscriber_count={} client={}",
            channel,
            remaining,
            getattr(websocket.client, "host", None),
        )

    async def publish(self, channel: str, event: dict[str, Any]) -> None:
        subscribers = list(self.subscribers.get(channel, set()))
        dead: list[WebSocket] = []
        logger.info(
            "开始发布 WebSocket 事件 channel={} fanout_count={} event_type={}",
            channel,
            len(subscribers),
            event.get("type"),
        )
        for websocket in subscribers:
            try:
                await websocket.send_json(event)
            except Exception as exc:
                logger.warning(
                    "发送 WebSocket JSON 失败 channel={} event_type={} client={} error={}",
                    channel,
                    event.get("type"),
                    getattr(websocket.client, "host", None),
                    exc,
                )
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(channel, websocket)
        if dead:
            logger.warning("已清理失效 WebSocket 连接 channel={} count={}", channel, len(dead))

    async def keepalive(self, websocket: WebSocket, channel: str) -> None:
        while True:
            try:
                message = await websocket.receive_text()
            except Exception as exc:
                logger.warning("WebSocket 接收消息失败 channel={} error={}", channel, exc)
                raise
            if message == "ping":
                logger.debug("收到 WebSocket 心跳 channel={}", channel)
                await websocket.send_text("pong")


GLOBAL_EVENT_BUS = EventBus()
