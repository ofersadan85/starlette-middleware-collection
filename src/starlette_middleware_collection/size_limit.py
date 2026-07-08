import os

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

ENV_VAR_NAME = "MW_REQUEST_BODY_LIMIT"


class SizeLimit(BaseHTTPMiddleware):
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
