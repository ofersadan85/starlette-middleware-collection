import logging
import os

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from starlette_middleware_collection import RequestLogging, RequestUUID
from starlette_middleware_collection.request_logging import DEFAULT_LOGGER_NAME, ENV_VAR_NAME


def setup_app(paired: bool = False, **kwargs) -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestLogging, **kwargs)
    if paired:
        app.add_middleware(RequestUUID)

    @app.get("/")
    async def _read_root(request: Request):
        return {"Hello": "World"}

    return app


def test_request_logging_default_logger(caplog):
    client = TestClient(setup_app())
    with caplog.at_level(logging.INFO, logger=DEFAULT_LOGGER_NAME):
        response = client.get("/")
    assert response.status_code == 200
    assert len(caplog.records) >= 1
    record = caplog.records[-1].msg
    assert isinstance(record, dict)
    assert record["method"] == "GET"
    assert record["path"] == "/"
    assert record["status_code"] == 200
    assert record["duration_ms"] >= 0


def test_request_logging_sync_handler():
    captured: list[dict] = []
    client = TestClient(setup_app(handler=captured.append))
    response = client.get("/")
    assert response.status_code == 200
    assert len(captured) == 1
    assert captured[0]["method"] == "GET"
    assert captured[0]["status_code"] == 200
    assert set(captured[0]) == {"request_id", "method", "path", "status_code", "duration_ms", "client"}


def test_request_logging_async_handler():
    captured: list[dict] = []

    async def handler(record: dict):
        captured.append(record)

    client = TestClient(setup_app(handler=handler))
    response = client.get("/")
    assert response.status_code == 200
    assert len(captured) == 1, "Async handler should have been awaited"
    assert captured[0]["path"] == "/"


def test_request_logging_custom_formatter():
    captured: list[str] = []

    def formatter(request, response, elapsed) -> str:
        return f"{request.method} {request.url.path} -> {response.status_code}"

    client = TestClient(setup_app(handler=captured.append, formatter=formatter))
    response = client.get("/")
    assert response.status_code == 200
    assert captured == ["GET / -> 200"]


def test_request_logging_captures_request_id_when_paired():
    captured: list[dict] = []
    client = TestClient(setup_app(paired=True, handler=captured.append))
    response = client.get("/")
    assert response.status_code == 200
    assert captured[0]["request_id"] is not None, "request_id should be populated by RequestUUID"


def test_request_logging_request_id_none_when_standalone():
    captured: list[dict] = []
    client = TestClient(setup_app(handler=captured.append))
    client.get("/")
    assert captured[0]["request_id"] is None


def test_request_logging_level_via_env_variable(caplog):
    os.environ[ENV_VAR_NAME] = str(logging.WARNING)
    try:
        client = TestClient(setup_app())
        with caplog.at_level(logging.DEBUG, logger=DEFAULT_LOGGER_NAME):
            client.get("/")
        assert caplog.records[-1].levelno == logging.WARNING
    finally:
        del os.environ[ENV_VAR_NAME]


def test_request_logging_handler_exception_does_not_break_request(caplog):
    def bad_handler(record: dict):
        raise RuntimeError("boom")

    client = TestClient(setup_app(handler=bad_handler))
    with caplog.at_level(logging.ERROR, logger=DEFAULT_LOGGER_NAME):
        response = client.get("/")
    assert response.status_code == 200
    assert any("failed to emit" in r.message for r in caplog.records)
