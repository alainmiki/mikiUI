"""Tests for enhanced API documentation and WebSocket features."""
import pytest
from fastapi.testclient import TestClient

from mikiui import Div, MikiApp
from mikiui.backend import create_app
from mikiui.backend.websocket import ConnectionManager


class TestOpenAPIMetadata:
    """Test that routes carry OpenAPI metadata."""

    def test_route_has_summary_from_docstring(self):
        app = MikiApp()

        @app.route("/items")
        def list_items():
            """Get all items."""
            return []

        route = app.routes["/items"]
        assert route.summary == "Get all items."

    def test_route_explicit_summary(self):
        app = MikiApp()

        @app.route("/items", summary="Custom summary", description="Custom desc", tags=["items"])
        def list_items():
            return []

        route = app.routes["/items"]
        assert route.summary == "Custom summary"
        assert route.description == "Custom desc"
        assert route.tags == ["items"]

    def test_route_typed_params(self):
        app = MikiApp()

        @app.route("/items/{item_id:int}")
        def get_item(ctx, item_id: int):
            return {"id": item_id}

        route = app.routes["/items/{item_id:int}"]
        assert len(route.path_params) == 1
        assert route.path_params[0].name == "item_id"
        assert route.path_params[0].type_name == "int"

    def test_get_route_pattern_matching(self):
        app = MikiApp()

        @app.route("/items/{item_id:int}")
        def get_item(ctx, item_id: int):
            return {"id": item_id}

        # Exact match should work
        route = app.routes["/items/{item_id:int}"]
        assert route is not None

        # Pattern match should work
        route = app.get_route("/items/42")
        assert route is not None
        assert route.name == "get_item"

        # Non-matching path should return None
        route = app.get_route("/other/42")
        assert route is None


class TestHTTPMethods:
    """Test new HTTP convenience methods."""

    def test_put_method(self):
        app = MikiApp()

        @app.put("/items/{item_id:int}")
        def update_item(ctx, item_id: int):
            return {"updated": item_id}

        client = TestClient(create_app(app, enable_csrf=False))
        resp = client.put("/items/42")
        assert resp.status_code == 200

    def test_delete_method(self):
        app = MikiApp()

        @app.delete("/items/{item_id:int}")
        def delete_item(ctx, item_id: int):
            return {"deleted": item_id}

        client = TestClient(create_app(app, enable_csrf=False))
        resp = client.delete("/items/42")
        assert resp.status_code == 200

    def test_patch_method(self):
        app = MikiApp()

        @app.patch("/items/{item_id:int}")
        def patch_item(ctx, item_id: int):
            return {"patched": item_id}

        client = TestClient(create_app(app, enable_csrf=False))
        resp = client.patch("/items/42")
        assert resp.status_code == 200


class TestWebSocketRooms:
    """Test WebSocket room/channel support."""

    def test_room_join_leave(self):
        mgr = ConnectionManager()

        class FakeWS:
            def __init__(self, user_id=None):
                self.state = type("S", (), {"mikiui_user_id": user_id, "mikiui_ip": "1.1.1.1"})()
                self.closed = False
            async def accept(self):
                pass

        ws1 = FakeWS("user1")
        ws2 = FakeWS("user2")

        mgr.active.append(ws1)
        mgr.active.append(ws2)

        mgr.join_room(ws1, "room-a")
        mgr.join_room(ws2, "room-a")
        mgr.join_room(ws1, "room-b")

        assert mgr.get_room_count("room-a") == 2
        assert mgr.get_room_count("room-b") == 1
        assert "room-a" in mgr.get_user_rooms(ws1)
        assert "room-b" in mgr.get_user_rooms(ws1)

        mgr.leave_room(ws1, "room-a")
        assert mgr.get_room_count("room-a") == 1
        assert "room-a" not in mgr.get_user_rooms(ws1)

    def test_room_cleanup_on_disconnect(self):
        mgr = ConnectionManager()

        class FakeWS:
            def __init__(self, user_id=None):
                self.state = type("S", (), {"mikiui_user_id": user_id, "mikiui_ip": "1.1.1.1"})()
            async def accept(self):
                pass

        ws = FakeWS("user1")
        mgr.active.append(ws)
        mgr.join_room(ws, "room-a")
        mgr.join_room(ws, "room-b")

        mgr.disconnect(ws)
        assert ws not in mgr.active
        assert mgr.get_room_count("room-a") == 0
        assert mgr.get_room_count("room-b") == 0


class TestRequestID:
    """Test request ID middleware."""

    def test_request_id_generated(self):
        app = MikiApp()

        @app.route("/")
        def home(ctx):
            return Div("ok")

        client = TestClient(create_app(app, enable_csrf=False))
        resp = client.get("/")
        assert "X-Request-ID" in resp.headers
        assert len(resp.headers["X-Request-ID"]) > 0

    def test_request_id_preserved(self):
        app = MikiApp()

        @app.route("/")
        def home(ctx):
            return Div("ok")

        client = TestClient(create_app(app, enable_csrf=False))
        custom_id = "my-custom-request-id-123"
        resp = client.get("/", headers={"X-Request-ID": custom_id})
        assert resp.headers["X-Request-ID"] == custom_id


class TestTestClient:
    """Test the MikiApp.test_client() helper."""

    def test_test_client_basic(self):
        app = MikiApp()

        @app.route("/")
        def home(ctx):
            return Div("hello")

        client = app.test_client(enable_csrf=False)
        resp = client.get("/")
        assert resp.status_code == 200
        assert "hello" in resp.text


class TestRouteGroupAuthPropagation:
    """Test that route group auth propagates to routes."""

    def test_group_auth_applied(self):
        from mikiui.router.auth import AuthRequirement

        app = MikiApp()
        api = app.route_group("/api")
        api.auth(AuthRequirement(strategy="session"))

        @api.get("/users")
        def list_users(ctx):
            return Div("users")

        route = app.routes["/api/users"]
        assert route.get_auth_requirement().strategy == "session"

    def test_route_override_group_auth(self):
        from mikiui.router.auth import AuthRequirement

        app = MikiApp()
        api = app.route_group("/api")
        api.auth(AuthRequirement(strategy="session"))

        @api.get("/public", auth=AuthRequirement(strategy="none"))
        def public_endpoint(ctx):
            return Div("public")

        route = app.routes["/api/public"]
        assert route.get_auth_requirement().strategy == "none"


class TestCLIVersion:
    """Test CLI --version flag."""

    def test_version_flag(self):
        from typer.testing import CliRunner

        from mikiui.cli.commands import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "MikiUI v" in result.output


class TestProjectNameValidation:
    """Test project name validation."""

    def test_valid_names(self):
        from mikiui.cli.commands import _validate_project_name
        assert _validate_project_name("myapp") == "myapp"
        assert _validate_project_name("my-app") == "my-app"
        assert _validate_project_name("my_app") == "my_app"
        assert _validate_project_name("  myapp  ") == "myapp"

    def test_invalid_names(self):
        from mikiui.cli.commands import _validate_project_name

        invalid = ["", "  ", "my/app", "my:app", "my<app", ".hidden", "-dash"]
        for name in invalid:
            with pytest.raises(ValueError):
                _validate_project_name(name)


class TestKeyboardNavigation:
    """Test keyboard accessibility of core widgets."""

    def test_tabs_keyboard_nav(self):
        from mikiui.components import Tabs

        tabs = Tabs([
            ("Tab A", "Content A"),
            ("Tab B", "Content B"),
            ("Tab C", "Content C"),
        ])
        html = str(tabs)
        assert 'role="tablist"' in html
        assert 'role="tab"' in html
        assert 'role="tabpanel"' in html
        assert 'tabindex="0"' in html
        assert 'tabindex="-1"' in html
        assert 'aria-selected="true"' in html
        assert 'aria-selected="false"' in html

    def test_menu_keyboard_attrs(self):
        from mikiui.widgets import MenuBar

        menubar = MenuBar(items=[
            ("File", [("New", "/new"), ("Open", "/open")]),
            ("Edit", [("Cut", "/cut")]),
        ])
        html = str(menubar)
        assert 'role="menubar"' in html
        assert 'role="menu"' in html
        assert 'role="menuitem"' in html
        assert 'aria-haspopup="true"' in html
        assert 'aria-expanded="false"' in html
        assert 'tabindex="-1"' in html

    def test_dialog_keyboard_attrs(self):
        from mikiui.components import Dialog

        dlg = Dialog("Content", title="Test", open=True)
        html = str(dlg)
        assert 'role="dialog"' in html
        assert 'aria-modal="true"' in html

    def test_form_labels(self):
        from mikiui.components import Form, Input

        form = Form(
            Input(name="email", aria_label="Email address"),
            method="POST",
        )
        html = str(form)
        assert 'aria-label="Email address"' in html

    def test_button_accessible(self):
        from mikiui.components import Button

        btn = Button("Submit", aria_label="Submit form")
        html = str(btn)
        assert 'aria-label="Submit form"' in html


class TestResponsiveCSS:
    """Test that responsive CSS rules are present."""

    def test_mobile_media_queries_exist(self):
        import os
        css_path = os.path.join(os.path.dirname(__file__), "..", "mikiui", "runtime", "miki.css")
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        assert "@media (max-width: 480px)" in css
        assert "@media (min-width: 481px) and (max-width: 768px)" in css
        assert "@media (hover: none)" in css

    def test_touch_css_rules(self):
        import os
        css_path = os.path.join(os.path.dirname(__file__), "..", "mikiui", "runtime", "miki.css")
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        assert "44px" in css
        assert "touch-action: manipulation" in css

    def test_safe_area_support(self):
        import os
        css_path = os.path.join(os.path.dirname(__file__), "..", "mikiui", "runtime", "miki.css")
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        assert "env(safe-area-inset-bottom)" in css

    def test_reduced_motion_support(self):
        import os
        css_path = os.path.join(os.path.dirname(__file__), "..", "mikiui", "runtime", "miki.css")
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        assert "prefers-reduced-motion" in css

    def test_viewport_height_fix(self):
        import os
        css_path = os.path.join(os.path.dirname(__file__), "..", "mikiui", "runtime", "miki.css")
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        assert "100dvh" in css
