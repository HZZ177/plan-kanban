from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from common.core.config import get_settings
from common.core.file_path import ensure_parent_directory
from common.models.base import Base

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_db() -> AsyncEngine:
    global _engine, _session_factory
    if _engine is not None and _session_factory is not None:
        return _engine

    settings = get_settings()
    db_path: Path = ensure_parent_directory(settings.sqlite_path)
    _engine = create_async_engine(settings.sqlite_url, future=True)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def get_engine() -> AsyncEngine:
    return init_db()


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    init_db()
    assert _session_factory is not None
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        yield session


async def ensure_schema() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        if conn.dialect.name != "sqlite":
            return

        result = await conn.exec_driver_sql("PRAGMA table_info(cards)")
        columns = {row[1] for row in result.fetchall()}
        if not columns:
            return

        missing_columns = {
            "summary": "summary TEXT NOT NULL DEFAULT ''",
            "owner": "owner VARCHAR(255) NOT NULL DEFAULT ''",
            "priority": "priority VARCHAR(16) NOT NULL DEFAULT 'P1'",
        }
        for column_name, ddl in missing_columns.items():
            if column_name not in columns:
                await conn.exec_driver_sql(f"ALTER TABLE cards ADD COLUMN {ddl}")


async def create_tables() -> None:
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await ensure_schema()


async def close_db() -> None:
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
