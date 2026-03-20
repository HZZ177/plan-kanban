from __future__ import annotations

from fastapi import APIRouter, WebSocket

from backend.app.ws.event_schema import build_ws_event

router = APIRouter()


@router.websocket("/issues")
async def issues_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(build_ws_event("issues.updated", "issues", {"connected": True}))
    await websocket.close()
