from __future__ import annotations

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, TimestampMixin


class ConversationEntry(TimestampMixin, Base):
    __tablename__ = "conversation_entries"

    session_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    execution_process_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    entry_type: Mapped[str] = mapped_column(String(64), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default="assistant")
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
