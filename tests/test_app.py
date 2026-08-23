"""Tests for building and serving a MikiUI app via the FastAPI backend."""

from __future__ import annotations

from fastapi.testclient import TestClient

from mikiui import Div, MikiApp
from mikiui.app.plugins import Plugin
from mikiui.backend import create_app


class MarkerPlugin(Plugin):
    def __init__(self):
        self.registered = False

    def register(self, app):
        self.registered = True

    def on_render(self, tree):
        tree.append(Div("PLUGIN_MARKER"))
        return tree


def make_app():
    app = MikiApp(title="Test App")

    @app.route("/")
    def home():
        return Div("home-page")

    @app.post("/inc")
    def inc(ctx):
        n = ctx.app.state.increment("count")
        return Div(f"count={n}")

    return app


def test_get_returns_full_page():
    app = make_app()
    client = TestClient(create_app(app))
    resp = client.get("/")
    assert resp.status_code == 200
    assert "<!doctype html>" in resp.text
    assert "home-page" in resp.text


def test_post_returns_full_page():
    app = make_app()
    client = TestClient(create_app(app))
    resp = client.post("/inc")
    assert resp.status_code == 200
    assert "count=1" in resp.text
    assert "<!doctype html>" in resp.text


def test_state_persists_across_requests():
    app = make_app()
    client = TestClient(create_app(app))
    assert "count=1" in client.post("/inc").text
    assert "count=2" in client.post("/inc").text


def test_plugin_registered_via_use():
    app = make_app()
    plugin = MarkerPlugin()
    app.use(plugin)
    assert plugin in app.plugins
    assert plugin.registered is True


def test_plugin_on_render_mutates_output():
    app = make_app()
    app.use(MarkerPlugin())
    client = TestClient(create_app(app))
    resp = client.get("/")
    assert "PLUGIN_MARKER" in resp.text


def test_hx_request_returns_fragment():
    app = make_app()
    client = TestClient(create_app(app))
    resp = client.get("/", headers={"HX-Request": "true"})
    assert "<!doctype html>" not in resp.text.lower()
    assert "home-page" in resp.text


def test_app_default_favicon():
    app = MikiApp(title="Test App")
    assert app.favicon == "/_miki/runtime/mikiui-icon.png"


def test_app_customizable_favicon():
    app = MikiApp(title="Test App", favicon="/custom/favicon.ico")
    assert app.favicon == "/custom/favicon.ico"


def test_page_includes_favicon():
    app = make_app()
    client = TestClient(create_app(app))
    resp = client.get("/")
    assert '<link rel="icon" href="/_miki/runtime/mikiui-icon.png"' in resp.text


def test_path_normalization_strips_trailing_slash():
    """Routes should normalize trailing slashes so /foo and /foo/ match."""
    app = MikiApp(title="Test")

    @app.route("/page")
    def page():
        return Div("content")

    assert "/page" in app.routes
    assert "/page/" not in app.routes


def test_root_path_not_stripped():
    """The root path '/' should never be stripped of its trailing slash."""
    app = MikiApp(title="Test")

    @app.route("/")
    def root():
        return Div("root")

    assert "/" in app.routes


def test_get_route_normalizes_path():
    """get_route should normalize lookup paths the same way routes are stored."""
    app = MikiApp(title="Test")

    @app.route("/items")
    def items():
        return Div("items")

    assert app.get_route("/items/") is not None
    assert app.get_route("/items") is not None
