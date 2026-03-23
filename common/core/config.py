from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Plan Kanban"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    LOG_RETENTION_DAYS: int = 7
    LOG_ROTATION_TIME: str = "00:00"
    LOG_DIR: str | None = None
    FRONTEND_DEV_PORT: int = 5173
    DB_PATH: str = ".dev/plan-kanban.db"
    CLAUDE_COMMAND: str = "claude"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def sqlite_path(self) -> Path:
        raw = Path(self.DB_PATH)
        if raw.is_absolute():
            return raw
        return self.project_root / raw

    @property
    def sqlite_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.sqlite_path.as_posix()}"

    @property
    def log_dir_path(self) -> Path:
        if self.LOG_DIR:
            raw = Path(self.LOG_DIR)
            if raw.is_absolute():
                return raw
            return self.project_root / raw
        return self.project_root / "logs"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
