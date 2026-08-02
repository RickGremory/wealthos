"""HTTP request timing middleware."""

from __future__ import annotations

import os
import time
import uuid
from collections.abc import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from wealthos.core.logging import get_logger
from wealthos.core.settings import get_settings

_log = get_logger("wealthos.http")


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Emit structured request latency logs and bind request_id for audit correlation."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        settings = get_settings()
        timing_on = settings.request_timing_enabled and not os.environ.get(
            "PYTEST_CURRENT_TEST"
        )
        if not timing_on:
            response = await call_next(request)
            response.headers["X-Request-Id"] = request_id
            return response

        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-Id"] = request_id
            return response
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            _log.info(
                "http_request",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
            )
