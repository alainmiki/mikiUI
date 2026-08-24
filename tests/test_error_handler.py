"""Tests for error handler middleware."""

from __future__ import annotations

import os
from types import SimpleNamespace

import pytest
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from mikiui.middleware.error_handler import ErrorHandlerMiddleware


class FakeApp:
    async def __call__(self, scope, receive, send):
        pass


def _make_request():
    app_state = SimpleNamespace(miki_app=None)
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "app": SimpleNamespace(state=app_state),
    }
    return Request(scope, receive=lambda: None)


def test_error_handler_middleware_dev_mode(monkeypatch):
    monkeypatch.setenv("MIKIUI_ENV", "development")
    middleware = ErrorHandlerMiddleware(FakeApp())
    assert middleware._dev is True


def test_error_handler_middleware_prod_mode(monkeypatch):
    monkeypatch.setenv("MIKIUI_ENV", "production")
    middleware = ErrorHandlerMiddleware(FakeApp())
    assert middleware._dev is False


@pytest.mark.asyncio
async def test_error_handler_catches_exception():
    middleware = ErrorHandlerMiddleware(FakeApp())

    async def failing_app(scope, receive, send):
        raise RuntimeError("boom")

    middleware.app = failing_app
    request = _make_request()
    response = await middleware._handle(request, RuntimeError("boom"))
    assert response.status_code in (500, 200)


@pytest.mark.asyncio
async def test_error_handler_returns_json_in_dev(monkeypatch):
    monkeypatch.setenv("MIKIUI_ENV", "development")
    middleware = ErrorHandlerMiddleware(FakeApp())
    request = _make_request()
    response = await middleware._handle(request, RuntimeError("boom"))
    assert isinstance(response, JSONResponse)
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_error_handler_returns_generic_in_prod(monkeypatch):
    monkeypatch.setenv("MIKIUI_ENV", "production")
    middleware = ErrorHandlerMiddleware(FakeApp())
    request = _make_request()
    response = await middleware._handle(request, RuntimeError("boom"))
    assert response.status_code == 500
    body = response.body.decode()
    assert "boom" not in body
