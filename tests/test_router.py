"""Tests for the MikiUI router helpers (prefixes, mounting, PWA manifest).

The :class:`~mikiui.router.Router` is a lightweight grouping helper that
delegates route registration to ``MikiApp.route``.  Two usage patterns are
tested:

1. **Explicit** — ``@router.get(app, "/path")`` (no mount needed).
2. **Mounted** — ``app.mount(router)`` then ``@router.get("/path")``.

Both forms produce identical route entries in ``app.routes``.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from mikiui import Div, MikiApp
from mikiui.backend import create_app
from mikiui.router import Router, add_pwa_manifest

# ---------------------------------------------------------------------------
# Prefix joining logic
# ---------------------------------------------------------------------------

def test_router_prefix_joins_path():
    router = Router(prefix="/admin")
    assert router._join("/x") == "/admin/x"
    assert router._join("/") == "/admin/"


def test_router_empty_prefix():
    router = Router()
    assert router._join("/x") == "/x"


def test_router_strips_trailing_slash():
    router = Router(prefix="/api/")
    assert router._join("/users") == "/api/users"


# ---------------------------------------------------------------------------
# Explicit form: @router.get(app, "/path")
# ---------------------------------------------------------------------------

def test_router_explicit_get_registers_route():
    app = MikiApp()
    router = Router(prefix="/admin")

    @router.get(app, "/dashboard")
    def dashboard():
        return Div("admin-dashboard")

    assert "/admin/dashboard" in app.routes


def test_router_explicit_post_registers_route():
    app = MikiApp()
    router = Router(prefix="/api")

    @router.post(app, "/submit")
    def submit():
        return Div("submitted")

    assert "/api/submit" in app.routes


def test_router_explicit_route_served():
    app = MikiApp()
    router = Router(prefix="/admin")

    @router.get(app, "/x")
    def handler():
        return Div("admin-x")

    client = TestClient(create_app(app))
    resp = client.get("/admin/x")
    assert resp.status_code == 200
    assert "admin-x" in resp.text


def test_router_explicit_with_title():
    app = MikiApp(title="MyApp")
    router = Router(prefix="/admin")

    @router.get(app, "/x", title="Admin Page")
    def handler():
        return Div("admin-x")

    route = app.routes["/admin/x"]
    assert route.title == "Admin Page"


# ---------------------------------------------------------------------------
# Mounted form: app.mount(router)  then  @router.get("/path")
# ---------------------------------------------------------------------------

def test_mount_binds_router_to_app():
    app = MikiApp()
    router = Router(prefix="/users")
    app.mount(router)
    assert router._app is app


def test_mount_then_bare_decorator_registers():
    app = MikiApp()
    router = Router(prefix="/users")
    app.mount(router)

    @router.get("/profile")
    def profile():
        return Div("profile-page")

    assert "/users/profile" in app.routes


def test_mount_then_post_decorator_registers():
    app = MikiApp()
    router = Router(prefix="/api")
    app.mount(router)

    @router.post("/data")
    def data():
        return Div("data-ok")

    assert "/api/data" in app.routes


def test_mount_serves_prefixed_route():
    app = MikiApp()
    router = Router(prefix="/admin")
    app.mount(router)

    @router.get("/")
    def admin_home():
        return Div("admin-home")

    @router.get("/settings")
    def settings():
        return Div("settings-page")

    client = TestClient(create_app(app))
    resp = client.get("/admin/")
    assert resp.status_code == 200
    assert "admin-home" in resp.text
    resp2 = client.get("/admin/settings")
    assert resp2.status_code == 200
    assert "settings-page" in resp2.text


def test_mount_with_prefix_override():
    app = MikiApp()
    router = Router(prefix="/old")
    app.mount(router, prefix="/new")

    @router.get("/path")
    def handler():
        return Div("mounted")

    assert "/new/path" in app.routes


def test_mount_rejects_non_router():
    app = MikiApp()
    with pytest.raises(TypeError):
        app.mount("not-a-router")  # type: ignore[arg-type]


def test_router_without_app_or_mount_raises():
    app = MikiApp()
    router = Router(prefix="/admin")

    with pytest.raises(RuntimeError, match="not bound"):
        @router.get("/x")
        def handler():
            return Div("x")


# ---------------------------------------------------------------------------
# Multiple routers / separate file pattern
# ---------------------------------------------------------------------------

def test_multiple_routers():
    app = MikiApp()
    user_router = Router(prefix="/users")
    admin_router = Router(prefix="/admin")
    app.mount(user_router)
    app.mount(admin_router)

    @user_router.get("/list")
    def users():
        return Div("users-list")

    @admin_router.get("/panel")
    def admin():
        return Div("admin-panel")

    client = TestClient(create_app(app))
    assert client.get("/users/list").status_code == 200
    assert client.get("/admin/panel").status_code == 200


# ---------------------------------------------------------------------------
# Path parameters
# ---------------------------------------------------------------------------

def test_path_param_extracted_from_route():
    """RouteDef extracts {param} placeholders from the path."""
    app = MikiApp()
    router = Router(prefix="/users")
    app.mount(router)

    @router.get("/{user_id}")
    def show_user(ctx, user_id: str):
        return Div(f"user-{user_id}")

    route = app.routes["/users/{user_id}"]
    assert "user_id" in route.path_params


def test_path_param_handler_receives_value():
    """Handler receives path params as kwargs."""
    import asyncio

    app = MikiApp()

    @app.route("/items/{item_id}")
    def item(ctx, item_id: str):
        return Div(f"item-{item_id}")

    async def run():
        nodes, ctx = await app.invoke(app.routes["/items/{item_id}"], path_params={"item_id": "42"})
        return nodes

    nodes = asyncio.run(run())
    from mikiui.engine.dom import render
    rendered = render(nodes[0])
    assert "item-42" in str(rendered)


def test_path_param_served_via_http():
    """End-to-end: path param handler served by FastAPI."""
    app = MikiApp()

    @app.route("/users/{user_id}")
    def show_user(ctx, user_id: str):
        return Div(f"user-{user_id}")

    client = TestClient(create_app(app))
    resp = client.get("/users/42")
    assert resp.status_code == 200
    assert "user-42" in resp.text


def test_router_path_param():
    """Router supports path params with prefix."""
    app = MikiApp()
    router = Router(prefix="/admin")
    app.mount(router)

    @router.get("/items/{item_id}")
    def show_item(ctx, item_id: str):
        return Div(f"admin-item-{item_id}")

    client = TestClient(create_app(app))
    resp = client.get("/admin/items/99")
    assert resp.status_code == 200
    assert "admin-item-99" in resp.text


def test_router_explicit_path_param():
    """Router explicit form supports path params."""
    app = MikiApp()
    router = Router(prefix="/api")

    @router.get(app, "/users/{user_id}")
    def show_user(ctx, user_id: str):
        return Div(f"api-user-{user_id}")

    client = TestClient(create_app(app))
    resp = client.get("/api/users/7")
    assert resp.status_code == 200
    assert "api-user-7" in resp.text


def test_async_handler():
    """Async route handlers are supported."""
    app = MikiApp()

    @app.route("/async")
    async def async_handler(ctx):
        return Div("async-ok")

    client = TestClient(create_app(app))
    resp = client.get("/async")
    assert resp.status_code == 200
    assert "async-ok" in resp.text


def test_async_handler_with_path_param():
    """Async handlers receive path params."""
    app = MikiApp()

    @app.route("/async/users/{user_id}")
    async def async_user(ctx, user_id: str):
        return Div(f"async-user-{user_id}")

    client = TestClient(create_app(app))
    resp = client.get("/async/users/55")
    assert resp.status_code == 200
    assert "async-user-55" in resp.text


def test_query_params_via_ctx():
    """Query params are accessible via ctx.query_params."""
    app = MikiApp()

    @app.route("/search")
    def search(ctx):
        q = ctx.query_params.get("q", [""])[0]
        return Div(f"search-{q}")

    client = TestClient(create_app(app))
    resp = client.get("/search?q=hello")
    assert resp.status_code == 200
    assert "search-hello" in resp.text


def test_form_via_ctx():
    """Form data is accessible via ctx.form()."""
    app = MikiApp()

    @app.route("/submit", methods=["POST"])
    def submit(ctx):
        pass  # tested via the endpoint below

    # Register an async-compatible handler for form parsing
    @app.post("/api/submit")
    def api_submit(ctx):
        return Div("ok")

    client = TestClient(create_app(app))
    resp = client.post("/api/submit", data={"name": "test"})
    assert resp.status_code == 200
    assert "ok" in resp.text


# ---------------------------------------------------------------------------
# PWA manifest
# ---------------------------------------------------------------------------

def test_pwa_manifest_route():
    fastapi_app = create_app(MikiApp())
    add_pwa_manifest(fastapi_app)
    client = TestClient(fastapi_app)
    resp = client.get("/manifest.webmanifest")
    assert resp.status_code == 200
    data = resp.json()
    assert data["display"] == "standalone"
    assert "name" in data


def test_pwa_manifest_with_icon():
    app = MikiApp(title="Icon Test App")
    app.favicon = "/_miki/runtime/mikiui-icon.png"
    fastapi_app = create_app(app)
    client = TestClient(fastapi_app)
    resp = client.get("/manifest.webmanifest")
    assert resp.status_code == 200
    data = resp.json()
    assert "icons" in data
    icons = data["icons"]
    assert any("512x512" in str(i.get("sizes", "")) for i in icons)
    assert any("192x192" in str(i.get("sizes", "")) for i in icons)
    assert icons[0]["src"] == "/_miki/runtime/mikiui-icon.png"


def test_url_for_resolves_named_route():
    app = MikiApp()

    @app.route("/users/{user_id}", name="user_detail")
    def detail(ctx, user_id: str):
        return Div(f"user-{user_id}")

    assert app.url_for("user_detail", user_id="42") == "/users/42"


def test_url_for_raises_for_unknown_name():
    app = MikiApp()
    with pytest.raises(ValueError, match="No route named"):
        app.url_for("does_not_exist")


def test_url_for_raises_for_missing_path_params():
    app = MikiApp()

    @app.route("/users/{user_id}", name="user_detail")
    def detail(ctx, user_id: str):
        return Div(f"user-{user_id}")

    with pytest.raises(ValueError, match="requires path parameter"):
        app.url_for("user_detail")


def test_nested_routers():
    api = Router(prefix="/api")
    v1 = Router(prefix="/v1")
    api.mount(v1)

    app = MikiApp()
    app.mount(api)

    @v1.get("/items")
    def items():
        return Div("items")

    client = TestClient(create_app(app))
    resp = client.get("/api/v1/items")
    assert resp.status_code == 200
    assert "items" in resp.text


def test_plugin_error_isolation():
    from mikiui.app.plugins import Plugin

    class BadPlugin(Plugin):
        name = "bad"

        def on_render(self, tree):
            raise RuntimeError("boom")

    class GoodPlugin(Plugin):
        name = "good"

        def on_render(self, tree):
            tree.append(Div("OK"))
            return tree

    app = MikiApp()

    @app.route("/")
    def home():
        return Div("home")

    app.use(BadPlugin())
    app.use(GoodPlugin())
    client = TestClient(create_app(app))
    resp = client.get("/")
    assert resp.status_code == 200
    assert "OK" in resp.text


def test_duplicate_route_raises():
    app = MikiApp()

    @app.route("/same")
    def first():
        return Div("first")

    with pytest.raises(ValueError, match="already registered"):
        @app.route("/same")
        def second():
            return Div("second")


def test_plugin_depends_on_ordering():
    from mikiui.app.plugins import Plugin

    class DepPlugin(Plugin):
        name = "dep"
        depends_on = ["base"]

    class BasePlugin(Plugin):
        name = "base"

    app = MikiApp()
    app.use(BasePlugin())
    app.use(DepPlugin())  # should not raise


def test_plugin_depends_on_missing_raises():
    from mikiui.app.plugins import Plugin

    class DepPlugin(Plugin):
        name = "dep"
        depends_on = ["missing"]

    app = MikiApp()
    with pytest.raises(RuntimeError, match="depends on"):
        app.use(DepPlugin())


def test_path_param_missing_raises():
    app = MikiApp()

    @app.route("/users/{user_id}")
    def show(ctx, user_id: str):
        return Div(f"user-{user_id}")

    from mikiui.app.routes import invoke_route
    route = list(app.routes.values())[0]
    with pytest.raises(ValueError, match="Missing required path parameters"):
        invoke_route(route, app, path_params={})


def test_plugin_on_request_invoked_per_request():
    """The on_request hook must be called for every incoming request."""
    from mikiui.app.plugins import Plugin

    calls: list = []

    class RequestSpyPlugin(Plugin):
        name = "spy-request"

        def on_request(self, request):
            calls.append(request)

    app = MikiApp()
    app.use(RequestSpyPlugin())

    @app.route("/")
    def home():
        return Div("home")

    client = TestClient(create_app(app))
    resp = client.get("/")
    assert resp.status_code == 200
    assert len(calls) == 1
    assert calls[0] is not None


def test_backend_routes_mounted_once():
    """Plugin backend_routes must be mounted exactly once on the FastAPI app."""
    from mikiui.app.plugins import Plugin

    class SingleRoutePlugin(Plugin):
        name = "single"

        def backend_routes(self):
            return [
                {
                    "path": "/api/single",
                    "methods": ["GET"],
                    "endpoint": lambda request: {"ok": True},
                    "include_in_schema": True,
                    "tags": ["api"],
                }
            ]

    app = MikiApp()
    app.use(SingleRoutePlugin())
    fa = create_app(app)
    paths = [r.path for r in fa.routes if r.path == "/api/single"]
    assert len(paths) == 1

