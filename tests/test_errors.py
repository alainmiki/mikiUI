"""Tests for MikiUI error handling."""

from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from mikiui.errors import (
    MikiUIError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    ValidationError,
    error_response,
    log_error,
)


class DummyRequest:
    """Minimal request stand-in for offline tests."""

    def __init__(self, path: str = "/test", method: str = "GET", accept: str = "application/json") -> None:
        self.url = type("U", (), {"path": path})()
        self.method = method
        self.headers = {"accept": accept}
        self.app = type("A", (), {"state": type("S", (), {"miki_app": None})()})()


class TestMikiUIError:
    def test_base_to_dict(self):
        err = MikiUIError()
        d = err.to_dict()
        assert d["error"] == "server_error"
        assert d["message"] == "An unexpected error occurred."


class TestValidationError:
    def test_to_dict(self):
        err = ValidationError({"field": "bad"})
        d = err.to_dict()
        assert d["error"] == "validation_error"
        assert d["fields"] == {"field": "bad"}


class TestNotFoundError:
    def test_default(self):
        err = NotFoundError()
        assert err.status_code == 404
        assert "resource" in str(err)

    def test_custom_resource(self):
        err = NotFoundError("user")
        assert err.status_code == 404


class TestPermissionError:
    def test_defaults(self):
        err = PermissionError()
        assert err.status_code == 403


class TestRateLimitError:
    def test_defaults(self):
        err = RateLimitError()
        assert err.status_code == 429
        assert err.retry_after == 60

    def test_custom_retry(self):
        err = RateLimitError(retry_after=120)
        assert err.retry_after == 120


class TestServerError:
    def test_defaults(self):
        err = ServerError()
        assert err.status_code == 500


class TestLogError:
    def test_logs_error(self, caplog):
        req = DummyRequest()
        log_error(ValueError("bad input"), req)
        assert "bad input" in caplog.text


class TestErrorResponse:
    def test_json_for_api(self):
        err = ValidationError({"f": "bad"})
        req = DummyRequest(path="/api/test", accept="application/json")
        resp = asyncio.run(error_response(err, req))
        assert resp.status_code == 422
        assert resp.headers["content-type"].startswith("application/json")

    def test_html_for_page(self):
        err = NotFoundError("page")
        req = DummyRequest(path="/test", accept="text/html")
        resp = asyncio.run(error_response(err, req))
        assert resp.status_code == 404
        assert resp.headers["content-type"].startswith("text/html")


class TestErrorHandlerMiddleware:
    def test_catches_miki_error(self):
        app = FastAPI()

        @app.get("/boom")
        def boom():
            raise ValidationError({"x": "bad"})

        from mikiui.middleware.error_handler import ErrorHandlerMiddleware
        app.add_middleware(ErrorHandlerMiddleware)

        client = TestClient(app)
        resp = client.get("/boom")
        assert resp.status_code == 422

    def test_catches_generic_exception(self):
        app = FastAPI()

        @app.get("/boom")
        def boom():
            raise RuntimeError("kaboom")

        from mikiui.middleware.error_handler import ErrorHandlerMiddleware
        app.add_middleware(ErrorHandlerMiddleware)

        client = TestClient(app)
        resp = client.get("/boom")
        assert resp.status_code == 500
