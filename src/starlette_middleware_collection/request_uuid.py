import os
from uuid import uuid4, uuid7

from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

ENV_VAR_NAME = "MW_UUID_VERSION"
SUPPORTED_VERSIONS = (4, 7)


class RequestUUID(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, dispatch: DispatchFunction | None = None, uuid_version: int | None = None) -> None:
        uuid_version = uuid_version or int(os.getenv(ENV_VAR_NAME, 7))  # Default to UUIDv7
        if uuid_version not in SUPPORTED_VERSIONS:
            raise ValueError(f"uuid_version not supported: {uuid_version}. Must be one of {SUPPORTED_VERSIONS}")
        self.uuid_function = uuid4 if uuid_version == 4 else uuid7
        super().__init__(app, dispatch)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.id = self.uuid_function()
        return await call_next(request)
