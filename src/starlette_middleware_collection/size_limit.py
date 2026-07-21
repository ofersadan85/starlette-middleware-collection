import os

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

ENV_VAR_NAME = "MW_REQUEST_BODY_LIMIT"


class SizeLimit(BaseHTTPMiddleware):
    """Rejects requests whose body exceeds a configured byte limit.

    Reads the incoming `content-length` header and returns
    `413 Content Too Large` when it exceeds `limit`, without touching the
    request body itself.

    Args:
        app: The ASGI application to wrap.
        dispatch: Optional custom dispatch function, forwarded to `BaseHTTPMiddleware`.
        limit: Maximum allowed request body size, in bytes. Falls back to the
            `MW_REQUEST_BODY_LIMIT` environment variable, then to 10 MB
            (`10 * 1024 * 1024`). The constructor argument always takes
            precedence over the environment variable.
    """

    def __init__(self, app: ASGIApp, dispatch: DispatchFunction | None = None, limit: int | None = None) -> None:
        self.limit = limit or int(os.getenv(ENV_VAR_NAME, 1024 * 1024 * 10))  # 10MB Default
        super().__init__(app, dispatch)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length = int(request.headers.get("content-length", 0))
        if self.limit is not None and content_length > self.limit:
            return Response(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                content=f"Request body too large ({content_length} > {self.limit})",
            )
        return await call_next(request)
