import os

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from starlette_middleware_collection import RequestUUID
from starlette_middleware_collection.request_uuid import ENV_VAR_NAME


def setup_app(uuid_version: int | None = None) -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestUUID, uuid_version=uuid_version)

    @app.post("/")
    async def _read_root(request: Request):
        return {"uuid": request.state.id}

    return app


def inner(client: TestClient):
    response = client.post("/")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert "uuid" in response.json()
    assert isinstance(response.json()["uuid"], str), "UUID should be a string"


def test_request_uuid():
    client = TestClient(setup_app())
    inner(client)


def test_request_uuid_with_env_variable():
    os.environ[ENV_VAR_NAME] = str(4)
    client = TestClient(setup_app())
    try:
        inner(client)
    finally:
        del os.environ[ENV_VAR_NAME]


def test_request_uuid_with_custom_version():
    custom_version = 4
    client = TestClient(setup_app(uuid_version=custom_version))
    inner(client)


def test_request_uuid_custom_version_overrides_env_variable():
    env_version = 1
    os.environ[ENV_VAR_NAME] = str(env_version)
    custom_version = 4
    client = TestClient(setup_app(uuid_version=custom_version))
    try:
        inner(client)
    finally:
        del os.environ[ENV_VAR_NAME]


@pytest.mark.parametrize("invalid_version", [1, 2, 3, 5, 6, 8, 9])
def test_request_uuid_invalid_versions(invalid_version):
    client = TestClient(setup_app(uuid_version=invalid_version))
    # Exception occurs during middleware initialization, not during app initialization
    # So we need to catch it on the first request to the app
    with pytest.raises(ValueError, match=r"^uuid_version not supported"):
        client.post("/")  # This will trigger the middleware and raise the ValueError
