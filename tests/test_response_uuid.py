import os

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from starlette_middleware_collection import RequestUUID, ResponseUUID
from starlette_middleware_collection.response_uuid import DEFAULT_HEADER, ENV_VAR_NAME


def setup_app(
    header_name: str | None = None, uuid_version: int | None = None, pair_ordered: bool | None = None
) -> FastAPI:
    app = FastAPI()
    if pair_ordered is True:
        app.add_middleware(ResponseUUID, header_name=header_name, uuid_version=uuid_version)
        app.add_middleware(RequestUUID)
    elif pair_ordered is False:
        app.add_middleware(RequestUUID)
        app.add_middleware(ResponseUUID, header_name=header_name, uuid_version=uuid_version)
    else:  # pair_ordered is None, add only ResponseUUID
        app.add_middleware(ResponseUUID, header_name=header_name, uuid_version=uuid_version)

    @app.get("/")
    async def _read_root(request: Request):
        return {"uuid": getattr(request.state, "id", None)}

    return app


def test_response_uuid_standalone_generates_header():
    client = TestClient(setup_app())
    response = client.get("/")
    assert response.status_code == 200
    assert DEFAULT_HEADER in response.headers
    assert len(response.headers[DEFAULT_HEADER]) > 0


def test_response_uuid_paired_propagates_request_id():
    client = TestClient(setup_app(pair_ordered=True))
    response = client.get("/")
    assert response.status_code == 200
    body_id = response.json()["uuid"]
    assert body_id is not None, "RequestUUID should have set request.state.id"
    assert response.headers[DEFAULT_HEADER] == body_id, "Response header should match the request id"


def test_response_uuid_paired_propagates_request_id_reversed():
    client = TestClient(setup_app(pair_ordered=False))
    response = client.get("/")
    assert response.status_code == 200
    body_id = response.json()["uuid"]
    assert body_id is not None, "RequestUUID should have set request.state.id"
    assert response.headers[DEFAULT_HEADER] == body_id, "Response header should match the request id"


def test_response_uuid_with_custom_header():
    custom_header = "X-Trace-Id"
    client = TestClient(setup_app(header_name=custom_header))
    response = client.get("/")
    assert custom_header in response.headers


def test_response_uuid_with_env_variable():
    env_header = "X-Env-Id"
    os.environ[ENV_VAR_NAME] = env_header
    client = TestClient(setup_app())
    try:
        response = client.get("/")
        assert env_header in response.headers
    finally:
        del os.environ[ENV_VAR_NAME]


def test_response_uuid_custom_header_overrides_env_variable():
    os.environ[ENV_VAR_NAME] = "X-Env-Id"
    custom_header = "X-Trace-Id"
    client = TestClient(setup_app(header_name=custom_header, pair_ordered=True))
    try:
        response = client.get("/")
        assert custom_header in response.headers
        assert "X-Env-Id" not in response.headers
    finally:
        del os.environ[ENV_VAR_NAME]


@pytest.mark.parametrize("invalid_version", [1, 2, 3, 5, 6, 8, 9])
def test_response_uuid_invalid_versions(invalid_version):
    client = TestClient(setup_app(uuid_version=invalid_version))
    with pytest.raises(ValueError, match=r"^uuid_version not supported"):
        client.get("/")
