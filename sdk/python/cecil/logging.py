from __future__ import annotations

import logging

LOGGER_NAME = "cecil"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.propagate = False
    return logger


def scrub(value: str | None) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    return f"{value[:3]}...{value[-1]}"
