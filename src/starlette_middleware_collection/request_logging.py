import inspect
import logging
import os
import time
from collections.abc import Awaitable, Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

ENV_VAR_NAME = "MW_REQUEST_LOG_LEVEL"
DEFAULT_LOGGER_NAME = "starlette_middleware_collection.request"

# The record can be a dict (default) or any custom structure returned by a formatter.
Handler = Callable[[Any], None] | Callable[[Any], Awaitable[None]]
Formatter = Callable[[Request, Response, float], Any]


class RequestLogging(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        dispatch: DispatchFunction | None = None,
        *,
        logger: logging.Logger | None = None,
        level: int | None = None,
        handler: Handler | None = None,
        formatter: Formatter | None = None,
    ) -> None:
        self.logger = logger or logging.getLogger(DEFAULT_LOGGER_NAME)
        self.level = level if level is not None else int(os.getenv(ENV_VAR_NAME, logging.INFO))
        self.handler = handler
        self.formatter = formatter
        super().__init__(app, dispatch)

    def default_record(self, request: Request, response: Response, elapsed: float) -> dict:
        return {
            "request_id": str(rid) if (rid := getattr(request.state, "id", None)) else None,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(elapsed * 1000, 3),
            "client": request.client.host if request.client else None,
        }

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start
        record = (
            self.formatter(request, response, elapsed)
            if self.formatter
            else self.default_record(request, response, elapsed)
        )
        try:
            if self.handler is not None:
                result = self.handler(record)
                if inspect.isawaitable(result):
                    await result
            else:
                self.logger.log(self.level, record)
        except Exception:  # logging must never break the request
            self.logger.exception("RequestLogging failed to emit record")
        return response
