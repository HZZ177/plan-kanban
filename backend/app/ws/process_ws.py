from __future__ import annotations

from fastapi import APIRouter, WebSocket

from backend.app.ws.event_schema import build_ws_event

router = APIRouter()


@router.websocket("/process")
async def process_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(build_ws_event("process.updated", "process", {"connected": True}))
    await websocket.close()
