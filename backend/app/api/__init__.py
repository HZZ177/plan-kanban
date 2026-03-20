from fastapi import APIRouter

from backend.app.api.acceptance_router import router as acceptance_router
from backend.app.api.action_router import router as action_router
from backend.app.api.card_router import router as card_router
from backend.app.api.chat_router import router as chat_router
from backend.app.api.diff_router import router as diff_router
from backend.app.api.file_router import router as file_router
from backend.app.api.health_router import router as health_router
from backend.app.api.kanban_router import router as kanban_router
from backend.app.api.process_router import router as process_router
from backend.app.api.session_router import router as session_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(card_router)
api_router.include_router(chat_router)
api_router.include_router(session_router)
api_router.include_router(process_router)
api_router.include_router(file_router)
api_router.include_router(diff_router)
api_router.include_router(acceptance_router)
api_router.include_router(action_router)
api_router.include_router(kanban_router)
