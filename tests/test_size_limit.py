import os

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from starlette_middleware_collection import SizeLimit
from starlette_middleware_collection.size_limit import ENV_VAR_NAME


def setup_app(limit: int | None = None) -> FastAPI:
    app = FastAPI()
    app.add_middleware(SizeLimit, limit=limit)

    @app.post("/")
    async def _read_root(_request: Request):
        return {"Hello": "World"}

    return app


def inner(client: TestClient, limit: int):
    small_body = "a" * (limit - 5)  # limit - 5 bytes for `body=`
    response = client.post("/", data={"body": small_body})
    assert response.status_code == 200, f"Expected status 200 on small request, got {response.status_code}"
    assert response.json() == {"Hello": "World"}

    # Test with a large request body
    large_body = "a" * (limit + 1)  # limit + 1 byte
    response = client.post("/", data={"body": large_body})
    assert response.status_code == 413, f"Expected status 413 on large request, got {response.status_code}"
    assert "Request body too large" in response.text


def test_size_limit():
    default_limit = 10 * 1024 * 1024  # 10MB
    client = TestClient(setup_app())
    inner(client, default_limit)


def test_size_limit_with_env_variable():
    test_limit = 1024 * 1024  # 1MB
    os.environ[ENV_VAR_NAME] = str(test_limit)
    client = TestClient(setup_app())
    try:
        inner(client, test_limit)
    finally:
        del os.environ[ENV_VAR_NAME]


def test_size_limit_with_custom_limit():
    custom_limit = 1024 * 1024 * 5  # 5MB
    client = TestClient(setup_app(limit=custom_limit))
    inner(client, custom_limit)


def test_size_limit_custom_limit_overrides_env_variable():
    env_limit = 1024 * 1024  # 1MB
    os.environ[ENV_VAR_NAME] = str(env_limit)
    custom_limit = 1024 * 1024 * 5  # 5MB
    client = TestClient(setup_app(limit=custom_limit))
    try:
        inner(client, custom_limit)
    finally:
        del os.environ[ENV_VAR_NAME]
