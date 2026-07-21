import os

from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from .request_uuid import uuid_function

ENV_VAR_NAME = "MW_RESPONSE_ID_HEADER"
DEFAULT_HEADER = "X-Api-Request-Id"


class ResponseUUID(BaseHTTPMiddleware):
    """Sets a request-id response header on every response.

    Propagates `request.state.id` when `RequestUUID` is also installed;
    otherwise generates a fresh id so the header is always present.

    Args:
        app: The ASGI application to wrap.
        dispatch: Optional custom dispatch function, forwarded to `BaseHTTPMiddleware`.
        header_name: Name of the response header to set. Falls back to the
            `MW_RESPONSE_ID_HEADER` environment variable, then to
            `"X-Api-Request-Id"`.
        uuid_version: `4` or `7`, used only when generating a fresh id.
            Falls back to the `MW_UUID_VERSION` environment variable, then
            to `7`.
    """

    def __init__(
        self,
        app: ASGIApp,
        dispatch: DispatchFunction | None = None,
        header_name: str | None = None,
        uuid_version: int | None = None,
    ) -> None:
        self.header_name = header_name or os.getenv(ENV_VAR_NAME, DEFAULT_HEADER)
        self.uuid_function = uuid_function(uuid_version)
        super().__init__(app, dispatch)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        # Propagate the RequestUUID id when present, otherwise generate a fresh one
        request_id = getattr(request.state, "id", None) or self.uuid_function()
        response.headers[self.header_name] = str(request_id)
        return response
