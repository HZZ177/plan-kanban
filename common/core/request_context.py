from __future__ import annotations

from contextvars import ContextVar
from typing import Any

# 请求上下文模块负责在 HTTP、后台任务与 WebSocket 链路之间传递 trace 与业务标识。
trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
card_id_var: ContextVar[str | None] = ContextVar("card_id", default=None)
session_id_var: ContextVar[str | None] = ContextVar("session_id", default=None)
execution_process_id_var: ContextVar[str | None] = ContextVar("execution_process_id", default=None)
channel_var: ContextVar[str | None] = ContextVar("channel", default=None)
transport_var: ContextVar[str | None] = ContextVar("transport", default=None)


def set_request_context(
    trace_id: str | None = None,
    request_id: str | None = None,
    card_id: str | None = None,
    session_id: str | None = None,
    execution_process_id: str | None = None,
    channel: str | None = None,
    transport: str | None = None,
) -> None:
    if trace_id is not None:
        trace_id_var.set(trace_id)
    if request_id is not None:
        request_id_var.set(request_id)
    if card_id is not None:
        card_id_var.set(card_id)
    if session_id is not None:
        session_id_var.set(session_id)
    if execution_process_id is not None:
        execution_process_id_var.set(execution_process_id)
    if channel is not None:
        channel_var.set(channel)
    if transport is not None:
        transport_var.set(transport)


def clear_request_context() -> None:
    trace_id_var.set(None)
    request_id_var.set(None)
    card_id_var.set(None)
    session_id_var.set(None)
    execution_process_id_var.set(None)
    channel_var.set(None)
    transport_var.set(None)


def get_trace_id() -> str | None:
    return trace_id_var.get()


def get_request_id() -> str | None:
    return request_id_var.get()


def get_request_context() -> dict[str, Any]:
    return {
        "trace_id": trace_id_var.get(),
        "request_id": request_id_var.get(),
        "card_id": card_id_var.get(),
        "session_id": session_id_var.get(),
        "execution_process_id": execution_process_id_var.get(),
        "channel": channel_var.get(),
        "transport": transport_var.get(),
    }


def copy_request_context() -> dict[str, Any]:
    return dict(get_request_context())


def apply_request_context(context: dict[str, Any] | None) -> None:
    if not context:
        return
    set_request_context(
        trace_id=context.get("trace_id"),
        request_id=context.get("request_id"),
        card_id=context.get("card_id"),
        session_id=context.get("session_id"),
        execution_process_id=context.get("execution_process_id"),
        channel=context.get("channel"),
        transport=context.get("transport"),
    )
