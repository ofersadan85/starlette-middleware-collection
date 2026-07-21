import os
from collections.abc import Callable
from uuid import UUID, uuid4, uuid7

from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

ENV_VAR_NAME = "MW_UUID_VERSION"
SUPPORTED_VERSIONS = (4, 7)


def uuid_function(version: int | None) -> Callable[[], UUID]:
    version = version or int(os.getenv(ENV_VAR_NAME, 7))  # Default to UUIDv7
    if version not in SUPPORTED_VERSIONS:
        raise ValueError(f"uuid_version not supported: {version}. Must be one of {SUPPORTED_VERSIONS}")
    return uuid4 if version == 4 else uuid7


class RequestUUID(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, dispatch: DispatchFunction | None = None, uuid_version: int | None = None) -> None:
        self.uuid_function = uuid_function(uuid_version)
        super().__init__(app, dispatch)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.id = self.uuid_function()
        return await call_next(request)
