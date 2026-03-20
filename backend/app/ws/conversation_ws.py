from __future__ import annotations

from fastapi import APIRouter, WebSocket

from backend.app.ws.event_schema import build_ws_event

router = APIRouter()


@router.websocket("/conversation")
async def conversation_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(build_ws_event("conversation.delta", "conversation", {"connected": True}))
    await websocket.close()
