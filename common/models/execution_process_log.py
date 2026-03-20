from __future__ import annotations

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, TimestampMixin


class ExecutionProcessLog(TimestampMixin, Base):
    __tablename__ = "execution_process_logs"

    execution_process_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    stream: Mapped[str] = mapped_column(String(32), nullable=False, default="stdout")
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, default="raw")
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
