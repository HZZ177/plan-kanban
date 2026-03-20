from __future__ import annotations

from fastapi import APIRouter, WebSocket

from backend.app.ws.event_schema import build_ws_event

router = APIRouter()


@router.websocket("/files")
async def files_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(build_ws_event("files.updated", "files", {"connected": True}))
    await websocket.close()
