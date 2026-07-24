"""Structured usecase timing helpers."""

from __future__ import annotations

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from wealthos.core.logging import get_logger
from wealthos.core.settings import get_settings

_log = get_logger("wealthos.timing")


@contextmanager
def timed(usecase: str, **context: Any) -> Iterator[None]:
    """Log wall-clock duration for a critical usecase when timing is enabled."""
    settings = get_settings()
    if not settings.request_timing_enabled or os.environ.get("PYTEST_CURRENT_TEST"):
        yield
        return

    started = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        _log.info(
            "usecase_timing",
            usecase=usecase,
            duration_ms=duration_ms,
            **context,
        )
