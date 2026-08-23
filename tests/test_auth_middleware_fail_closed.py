"""Tests for auth middleware fail-closed behavior and static asset security."""

from __future__ import annotations

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse

from mikiui.router.auth import AuthRequirement
from mikiui.router.auth_middleware import AuthMiddleware


class FakeRequest:
    def __init__(self, headers=None, cookies=None, url="/test"):
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.url = url
        self.state = type("State", (), {"mikiui_user": None})()


def test_auth_middleware_fails_closed_when_strategy_missing():
    app = type("FakeApp", (), {"get_auth_strategy": lambda self, name: None})()
    middleware = AuthMiddleware(app)
    route = type("Route", (), {"_auth_requirement": AuthRequirement(strategy="jwt"), "requires_auth": False})()
    request = FakeRequest()
    response = middleware.enforce(request, route)
    assert response is not None
    assert response.status_code == 503
    body = response.body.decode()
    assert "Auth infrastructure not configured" in body


def test_auth_middleware_allows_public_route():
    app = type("FakeApp", (), {"get_auth_strategy": lambda self, name: None})()
    middleware = AuthMiddleware(app)
    route = type("Route", (), {"_auth_requirement": AuthRequirement(strategy="none"), "requires_auth": False})()
    request = FakeRequest()
    assert middleware.enforce(request, route) is None


def test_auth_middleware_returns_401_when_user_invalid():
    class FakeStrategy:
        def validate(self, request):
            return None

    app = type("FakeApp", (), {"get_auth_strategy": lambda self, name: FakeStrategy() if name == "session" else None})()
    middleware = AuthMiddleware(app)
    route = type("Route", (), {"_auth_requirement": AuthRequirement(strategy="session"), "requires_auth": False})()
    request = FakeRequest(headers={"HX-Request": "true"})
    response = middleware.enforce(request, route)
    assert response.status_code == 401
    assert response.headers.get("HX-Redirect") == "/login"


def test_auth_middleware_sets_user_on_success():
    class FakeStrategy:
        def validate(self, request):
            return {"user_id": "u1"}

    app = type("FakeApp", (), {"get_auth_strategy": lambda self, name: FakeStrategy() if name == "session" else None})()
    middleware = AuthMiddleware(app)
    route = type("Route", (), {"_auth_requirement": AuthRequirement(strategy="session"), "requires_auth": False})()
    request = FakeRequest()
    response = middleware.enforce(request, route)
    assert response is None
    assert request.state.mikiui_user == {"user_id": "u1"}
