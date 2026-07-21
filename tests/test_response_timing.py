import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from starlette_middleware_collection import ResponseTime
from starlette_middleware_collection.response_timing import DEFAULT_HEADER, ENV_VAR_NAME


def setup_app(header_name: str | None = None) -> FastAPI:
    app = FastAPI()
    app.add_middleware(ResponseTime, header_name=header_name)

    @app.get("/")
    async def _read_root():
        return {"Hello": "World"}

    return app


def inner(client: TestClient, header_name: str):
    response = client.get("/")
    assert response.status_code == 200, f"Expected status 200, got {response.status_code}"
    assert header_name in response.headers, f"Expected header {header_name} in response"
    value = float(response.headers[header_name])  # Must parse as a float (seconds)
    assert value >= 0, f"Timing value should be non-negative, got {value}"


def test_response_timing():
    client = TestClient(setup_app())
    inner(client, DEFAULT_HEADER)


def test_response_timing_with_custom_header():
    custom_header = "X-Custom-Time"
    client = TestClient(setup_app(header_name=custom_header))
    inner(client, custom_header)


def test_response_timing_with_env_variable():
    env_header = "X-Env-Time"
    os.environ[ENV_VAR_NAME] = env_header
    client = TestClient(setup_app())
    try:
        inner(client, env_header)
    finally:
        del os.environ[ENV_VAR_NAME]


def test_response_timing_custom_header_overrides_env_variable():
    os.environ[ENV_VAR_NAME] = "X-Env-Time"
    custom_header = "X-Custom-Time"
    client = TestClient(setup_app(header_name=custom_header))
    try:
        inner(client, custom_header)
    finally:
        del os.environ[ENV_VAR_NAME]
