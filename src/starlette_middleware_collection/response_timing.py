import os
import time

from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

ENV_VAR_NAME = "MW_TIMING_HEADER"
DEFAULT_HEADER = "X-Process-Time"


class ResponseTime(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, dispatch: DispatchFunction | None = None, header_name: str | None = None) -> None:
        self.header_name = header_name or os.getenv(ENV_VAR_NAME, DEFAULT_HEADER)
        super().__init__(app, dispatch)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        response.headers[self.header_name] = f"{time.perf_counter() - start:.6f}"  # Seconds
        return response
