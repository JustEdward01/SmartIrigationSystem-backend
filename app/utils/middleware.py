"""Custom middleware utilities."""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Log each incoming request path and status code."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        logging.info("%s %s -> %s", request.method, request.url.path, response.status_code)
        return response

