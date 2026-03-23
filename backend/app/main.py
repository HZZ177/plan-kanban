from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import api_router
from backend.app.middleware.error_middleware import ErrorMiddleware
from backend.app.middleware.http_log_middleware import HttpLogMiddleware
from backend.app.ws import ws_router
from common.core.config import get_settings
from common.core.database import close_db, create_tables, init_db
from common.core.logger import logger

# 应用入口负责组装 FastAPI、注册中间件与路由，并在生命周期内输出启动/停止日志。
if sys.platform == "win32" and hasattr(asyncio, "WindowsProactorEventLoopPolicy"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("应用启动 app_name={}", settings.APP_NAME)
    init_db()
    await create_tables()
    yield
    await close_db()
    logger.info("应用停止 app_name={}", settings.APP_NAME)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
    app.add_middleware(ErrorMiddleware)
    app.add_middleware(HttpLogMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    app.include_router(ws_router)
    return app


app = create_app()


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "backend.app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
