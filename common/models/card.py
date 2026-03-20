from __future__ import annotations

from sqlalchemy import Boolean, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, TimestampMixin


class Card(TimestampMixin, Base):
    __tablename__ = "cards"

    project_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    owner: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    priority: Mapped[str] = mapped_column(String(16), nullable=False, default="P1")
    raw_requirement: Mapped[str] = mapped_column(Text, nullable=False)
    current_stage: Mapped[str] = mapped_column(String(32), nullable=False, default="raw")
    acceptance_substate: Mapped[str | None] = mapped_column(String(64), nullable=True)
    plan_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    issues_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    latest_session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    active_process_type: Mapped[str] = mapped_column(String(64), nullable=False, default="none")
    active_process_status: Mapped[str] = mapped_column(String(32), nullable=False, default="idle")
    active_process_session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    worktree_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    branch_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
