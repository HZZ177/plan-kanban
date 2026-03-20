from __future__ import annotations

import logging
from functools import lru_cache

from common.core.config import get_settings


def _level_from_name(name: str) -> int:
    return getattr(logging, name.upper(), logging.INFO)


@lru_cache(maxsize=1)
def _configure_logger() -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger("plan_kanban")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        logger.addHandler(handler)
    logger.setLevel(_level_from_name(settings.LOG_LEVEL))
    logger.propagate = False
    return logger


logger = _configure_logger()
