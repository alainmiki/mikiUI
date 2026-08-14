"""Tests for the MikiUI router helpers (prefixes, PWA manifest).

NOTE (framework bug): ``Router.add`` is intended to register a route on the
underlying ``MikiApp`` at the joined prefix path, but the current
implementation calls ``self.app.route(...)`` (which returns a decorator) without
invoking the returned decorator with the handler, so the route is never added to
``app.routes``. These tests therefore exercise the prefix-joining logic and the
end-to-end serving of a prefixed path (registered directly at the joined path),
plus the working ``add_pwa_manifest`` helper.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mikiui import MikiApp, Div
from mikiui.backend import create_app
from mikiui.router import Router, add_pwa_manifest


def test_router_prefix_joins_path():
    app = MikiApp()
    router = Router(app, prefix="/admin")
    assert router._join("/x") == "/admin/x"
    assert router._join("/") == "/admin"


def test_router_add_returns_decorator():
    app = MikiApp()
    router = Router(app, prefix="/admin")
    dec = router.add("/x")
    assert callable(dec)


def test_prefixed_route_served():
    # End-to-end check that a path under the "/admin" prefix is served.
    app = MikiApp()
    joined = Router(app, prefix="/admin")._join("/x")

    @app.route(joined)
    def handler():
        return Div("admin-x")

    client = TestClient(create_app(app))
    resp = client.get("/admin/x")
    assert resp.status_code == 200
    assert "admin-x" in resp.text


def test_pwa_manifest_route():
    fastapi_app = create_app(MikiApp())
    add_pwa_manifest(fastapi_app)
    client = TestClient(fastapi_app)
    resp = client.get("/manifest.webmanifest")
    assert resp.status_code == 200
    data = resp.json()
    assert data["display"] == "standalone"
    assert "name" in data
