from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, TimestampMixin


class IssueIndex(TimestampMixin, Base):
    __tablename__ = "issue_index"

    card_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    issue_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    priority: Mapped[str] = mapped_column(String(8), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    refs: Mapped[str] = mapped_column(Text, nullable=False)
    dev_state: Mapped[str] = mapped_column(String(16), nullable=False, default="未开始")
    test_state: Mapped[str] = mapped_column(String(16), nullable=False, default="未开始")
    owner: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
