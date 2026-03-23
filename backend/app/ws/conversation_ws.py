from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.ws.event_bus import GLOBAL_EVENT_BUS
from backend.app.ws.patch_stream import build_ready_event
from common.core.logger import logger
from common.core.request_context import clear_request_context, set_request_context

router = APIRouter()


# conversation 频道负责把聊天消息与运行中的助手输出推送到前端。
@router.websocket("/conversation")
async def conversation_ws(websocket: WebSocket) -> None:
    trace_id = websocket.query_params.get("trace_id")
    request_id = websocket.query_params.get("request_id")
    set_request_context(trace_id=trace_id, request_id=request_id, channel="conversation", transport="ws")
    logger.info("收到 WebSocket 连接请求 channel=conversation trace_id={} request_id={}", trace_id, request_id)
    await GLOBAL_EVENT_BUS.connect("conversation", websocket)
    try:
        await websocket.send_json(build_ready_event("conversation", {"connected": True}))
        logger.info("已发送 WebSocket 就绪事件 channel=conversation")
        await GLOBAL_EVENT_BUS.keepalive(websocket, "conversation")
    except WebSocketDisconnect as exc:
        logger.info("WebSocket 已断开 channel=conversation code={}", exc.code)
    except Exception:
        logger.exception("conversation WebSocket 循环执行失败")
        raise
    finally:
        GLOBAL_EVENT_BUS.disconnect("conversation", websocket)
        clear_request_context()
