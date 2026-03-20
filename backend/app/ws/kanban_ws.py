from __future__ import annotations

from fastapi import APIRouter, WebSocket

from backend.app.ws.event_schema import build_ws_event

router = APIRouter()


@router.websocket("/kanban")
async def kanban_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(build_ws_event("kanban.updated", "kanban", {"connected": True}))
    await websocket.close()
