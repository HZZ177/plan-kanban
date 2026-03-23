from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.ws.event_bus import GLOBAL_EVENT_BUS
from backend.app.ws.patch_stream import build_ready_event
from common.core.logger import logger
from common.core.request_context import clear_request_context, set_request_context

router = APIRouter()


# process 频道负责推送卡片当前进程状态变化。
@router.websocket("/process")
async def process_ws(websocket: WebSocket) -> None:
    trace_id = websocket.query_params.get("trace_id")
    request_id = websocket.query_params.get("request_id")
    set_request_context(trace_id=trace_id, request_id=request_id, channel="process", transport="ws")
    logger.info("收到 WebSocket 连接请求 channel=process trace_id={} request_id={}", trace_id, request_id)
    await GLOBAL_EVENT_BUS.connect("process", websocket)
    try:
        await websocket.send_json(build_ready_event("process", {"connected": True}))
        logger.info("已发送 WebSocket 就绪事件 channel=process")
        await GLOBAL_EVENT_BUS.keepalive(websocket, "process")
    except WebSocketDisconnect as exc:
        logger.info("WebSocket 已断开 channel=process code={}", exc.code)
    except Exception:
        logger.exception("process WebSocket 循环执行失败")
        raise
    finally:
        GLOBAL_EVENT_BUS.disconnect("process", websocket)
        clear_request_context()
