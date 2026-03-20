from fastapi import APIRouter

from backend.app.ws.conversation_ws import router as conversation_ws_router
from backend.app.ws.files_ws import router as files_ws_router
from backend.app.ws.issues_ws import router as issues_ws_router
from backend.app.ws.kanban_ws import router as kanban_ws_router
from backend.app.ws.process_ws import router as process_ws_router

ws_router = APIRouter(prefix="/ws")
ws_router.include_router(conversation_ws_router)
ws_router.include_router(process_ws_router)
ws_router.include_router(issues_ws_router)
ws_router.include_router(files_ws_router)
ws_router.include_router(kanban_ws_router)
