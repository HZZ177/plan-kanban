from __future__ import annotations

import sys
import threading
from functools import lru_cache
from typing import Any

from loguru import logger as _loguru_logger

from common.core.config import get_settings
from common.core.file_path import logs_path
from common.core.request_context import get_request_context


# 全局日志模块负责初始化 loguru，并把请求上下文字段注入到每条日志记录中。
def _context_filter(record: dict[str, Any]) -> bool:
    context = get_request_context()
    record["extra"]["trace_id"] = context.get("trace_id") or "-"
    record["extra"]["request_id"] = context.get("request_id") or "-"
    record["extra"]["card_id"] = context.get("card_id") or "-"
    record["extra"]["session_id"] = context.get("session_id") or "-"
    record["extra"]["execution_process_id"] = context.get("execution_process_id") or "-"
    record["extra"]["channel"] = context.get("channel") or "-"
    record["extra"]["transport"] = context.get("transport") or "-"
    return True


@lru_cache(maxsize=1)
def _configure_logger():
    settings = get_settings()
    _loguru_logger.remove()
    log_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level:<4} | "
        "trace={extra[trace_id]} | "
        "{module}:{line} | {message}"
    )
    _loguru_logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL.upper(),
        format=log_format,
        colorize=True,
        filter=_context_filter,
        enqueue=False,
        backtrace=settings.DEBUG,
        diagnose=settings.DEBUG,
    )
    _loguru_logger.add(
        str(logs_path / "app_{time:YYYY-MM-DD}.log"),
        level=settings.LOG_LEVEL.upper(),
        format=log_format,
        rotation=settings.LOG_ROTATION_TIME,
        retention=f"{settings.LOG_RETENTION_DAYS} days",
        compression="zip",
        encoding="utf-8",
        filter=_context_filter,
        enqueue=False,
        backtrace=True,
        diagnose=settings.DEBUG,
    )
    sys.excepthook = _handle_uncaught_exception
    if hasattr(threading, "excepthook"):
        threading.excepthook = _handle_thread_exception
    return _loguru_logger


def _handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    _loguru_logger.opt(exception=(exc_type, exc_value, exc_traceback)).error("未捕获的异常")


def _handle_thread_exception(args: threading.ExceptHookArgs) -> None:
    if issubclass(args.exc_type, KeyboardInterrupt):
        return
    _loguru_logger.opt(
        exception=(args.exc_type, args.exc_value, args.exc_traceback)
    ).error("线程中未捕获的异常")


logger = _configure_logger()

__all__ = ["logger"]
