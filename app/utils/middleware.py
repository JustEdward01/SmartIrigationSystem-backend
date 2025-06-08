"""Custom middleware utilities."""

import logging
from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Log incoming requests with timing and payload snippet."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = perf_counter()
        body = await request.body()
        response = await call_next(request)
        duration_ms = (perf_counter() - start) * 1000
        logging.info(
            "%s %s %s %.1fms payload=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            body[:200],
        )
        return response

