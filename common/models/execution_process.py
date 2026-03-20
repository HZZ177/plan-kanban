from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, TimestampMixin


class ExecutionProcess(TimestampMixin, Base):
    __tablename__ = "execution_processes"

    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    run_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    executor_action: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="running")
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dropped: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
