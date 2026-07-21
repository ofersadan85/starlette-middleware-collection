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
    """Logs one record per request.

    By default logs a structured dict to a standard-library logger; pass a
    `formatter` to customize the record and/or a `handler` (sync or async)
    to route it anywhere instead. Pairs with `RequestUUID`: when
    `request.state.id` is set, it is included as `request_id`.

    Args:
        app: The ASGI application to wrap.
        dispatch: Optional custom dispatch function, forwarded to `BaseHTTPMiddleware`.
        logger: Logger to log to when no `handler` is given. Defaults to
            `logging.getLogger("starlette_middleware_collection.request")`.
        level: Log level to use when no `handler` is given. Falls back to
            the `MW_REQUEST_LOG_LEVEL` environment variable, then to
            `logging.INFO`.
        handler: Optional sync or async callable that receives each record
            instead of the logger, e.g. to write to a file, database, or
            queue. A failing handler is caught and logged; it never breaks
            the request.
        formatter: Optional callable `(request, response, elapsed) -> Any`
            that builds the record. Defaults to `default_record`.
    """

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
        self.handler = handler or self._default_handler
        self.formatter = formatter or self._default_record
        super().__init__(app, dispatch)

    def _default_handler(self, record: Any) -> None:
        self.logger.log(self.level, record)

    def _default_record(self, request: Request, response: Response, elapsed: float) -> dict:
        """Build the default log record for a request/response pair.

        Args:
            request: The incoming request.
            response: The outgoing response.
            elapsed: Request duration, in seconds.

        Returns:
            A dict with `request_id`, `method`, `path`, `status_code`,
            `duration_ms`, and `client`.
        """
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
        try:
            record = self.formatter(request, response, elapsed)
            result = self.handler(record)
            if inspect.isawaitable(result):
                await result
        except Exception:  # logging must never break the request
            self.logger.exception("RequestLogging failed to emit record")
        return response
