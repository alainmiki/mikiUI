"""Tests for RouteGroup naming collision fix and auth resolution."""

from __future__ import annotations

from typing import Any

from mikiui.router.auth import AuthRequirement
from mikiui.router.group import RouteGroup, RouteGroupBuilder


class FakeApp:
    def __init__(self):
        self.routes: dict[str, Any] = {}
        self._auth_strategies: dict[str, Any] = {}

    def route(self, path, **kwargs):
        self.routes[path] = kwargs
        return lambda fn: fn

    def register_auth_strategy(self, name, strategy):
        self._auth_strategies[name] = strategy

    def get_auth_strategy(self, name):
        return self._auth_strategies.get(name)


def test_route_group_auth_method_can_be_called_multiple_times():
    app = FakeApp()
    group = RouteGroup(app, "/api")
    req1 = AuthRequirement(strategy="jwt")
    req2 = AuthRequirement(strategy="session")
    group.auth(req1)
    group.auth(req2)
    assert group._auth == req2
    resolved = group._resolve_auth(None)
    assert resolved == req2


def test_route_group_rate_limit_can_be_called_multiple_times():
    app = FakeApp()
    group = RouteGroup(app, "/api")
    group.rate_limit(limit=10, window=60)
    group.rate_limit(limit=20, window=120)
    assert group._rate_limit.limit == 20
    assert group._rate_limit.window == 120


def test_route_group_csrf_can_be_called_multiple_times():
    app = FakeApp()
    group = RouteGroup(app, "/api")
    group.csrf(exempt_paths=["/health"])
    group.csrf(exempt_paths=["/webhook"], exempt_methods=("POST",))
    assert group._csrf.exempt_paths == ("/webhook",)
    assert group._csrf.exempt_methods == ("POST",)


def test_route_group_builder_auth_fluent():
    app = FakeApp()
    builder = RouteGroupBuilder(app, "/admin")
    result = builder.auth(AuthRequirement(strategy="jwt"))
    assert result is builder
    assert builder._group._auth.strategy == "jwt"


def test_route_group_resolve_auth_route_override():
    app = FakeApp()
    group = RouteGroup(app, "/api", auth=AuthRequirement(strategy="jwt"))
    route_req = AuthRequirement(strategy="session")
    assert group._resolve_auth(route_req) == route_req


def test_route_group_resolve_auth_boolean_false():
    app = FakeApp()
    group = RouteGroup(app, "/api")
    result = group._resolve_auth(False)
    assert result.strategy == "none"


def test_route_group_resolve_auth_boolean_true_falls_back_to_group():
    app = FakeApp()
    group = RouteGroup(app, "/api", auth=AuthRequirement(strategy="jwt"))
    result = group._resolve_auth(True)
    assert result.strategy == "jwt"


def test_route_group_resolve_auth_boolean_true_no_group_defaults_session():
    app = FakeApp()
    group = RouteGroup(app, "/api")
    result = group._resolve_auth(True)
    assert result.strategy == "session"
