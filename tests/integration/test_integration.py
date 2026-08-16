"""Integration tests for MikiUI app lifecycle, routes, plugins, themes, and builds."""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from mikiui import Div, MikiApp
from mikiui.app.plugins import ComponentPlugin, Plugin, WidgetPlugin
from mikiui.backend.server import create_app
from mikiui.build.desktop_build import build_desktop
from mikiui.build.web_build import build_web


@pytest.fixture()
def app() -> MikiApp:
    return MikiApp(title="Integration Test App")


class TestAppLifecycle:
    def test_create_and_configure(self):
        app = MikiApp(title="Lifecycle Test")
        assert app.title == "Lifecycle Test"
        assert app.theme == "light"
        assert app.plugins == []

    def test_plugin_registration_and_hooks(self):
        calls: list[str] = []

        class HookPlugin(Plugin):
            name = "hook"

            def register(self, app):
                calls.append("register")

            def on_render(self, tree):
                calls.append("on_render")
                return tree

            def on_route_add(self, path, methods, handler):
                calls.append("on_route_add")

        app = MikiApp()
        app.use(HookPlugin())

        @app.route("/test", methods=("GET",))
        def test_route():
            return Div("test")

        assert "register" in calls
        assert "on_route_add" in calls

        with TestClient(create_app(app)) as client:
            resp = client.get("/test")
            assert resp.status_code == 200

        assert "on_render" in calls

    def test_shutdown_calls_on_shutdown(self):
        shutdown_calls: list[str] = []

        class ShutdownPlugin(Plugin):
            name = "shutdown"

            def on_shutdown(self):
                shutdown_calls.append("shutdown")

        app = MikiApp()
        app.use(ShutdownPlugin())
        app.shutdown()
        assert "shutdown" in shutdown_calls

    def test_plugin_configuration(self):
        class ConfigPlugin(Plugin):
            name = "config"
            config: dict = {}

            def configure(self, config):
                self.config = config

        app = MikiApp()
        plugin = ConfigPlugin()
        app.use(plugin, config={"key": "value"})
        assert plugin.config == {"key": "value"}


class TestRouteIntegration:
    def test_route_with_path_params(self, app):
        @app.route("/users/{user_id}", methods=("GET",))
        def get_user(ctx, user_id):
            return Div(f"User {user_id}")

        with TestClient(create_app(app)) as client:
            resp = client.get("/users/42")
            assert resp.status_code == 200
            assert "User 42" in resp.text

    def test_route_requires_auth(self, app):
        from mikiui_app_plugins.session import SessionPlugin

        session = SessionPlugin(secret_key="a-very-long-secret-key-for-testing")
        app.use(session)

        @app.route("/secret", methods=("GET",), requires_auth=True)
        def secret():
            return Div("secret data")

        with TestClient(create_app(app)) as client:
            resp = client.get("/secret")
            assert resp.status_code == 401

    def test_post_route_with_query_data(self, app):
        @app.route("/api/items", methods=("POST",))
        def create_item(ctx):
            name = ctx.query_params.get("name", ["unknown"])[0]
            return Div(f"Created {name}")

        with TestClient(create_app(app)) as client:
            resp = client.post("/api/items?name=Widget")
            assert resp.status_code == 200
            assert "Created Widget" in resp.text


class TestPluginIntegration:
    def test_widget_plugin_registration(self, app):
        class MyWidget:
            pass

        class MyPlugin(WidgetPlugin):
            name = "my"

            def widgets(self):
                return {"MyWidget": MyWidget}

        app.use(MyPlugin())
        assert "my:MyWidget" in app.registry.list_registered()
        assert app.registry.get("MyWidget") is MyWidget

    def test_component_plugin_registration(self, app):
        class MyComponent:
            pass

        class MyPlugin(ComponentPlugin):
            name = "my"

            def components(self):
                return {"MyComponent": MyComponent}

        app.use(MyPlugin())
        assert "my:MyComponent" in app.registry.list_registered()
        assert app.registry.get("MyComponent") is MyComponent

    def test_multiple_plugins_dependencies(self):
        class BasePlugin(Plugin):
            name = "base"

        class DependentPlugin(Plugin):
            name = "dependent"
            depends_on = ["base"]

        app = MikiApp()
        app.use(BasePlugin())
        app.use(DependentPlugin())

        with pytest.raises(RuntimeError, match="depends on"):
            app2 = MikiApp()
            app2.use(DependentPlugin())

    def test_plugin_backend_routes(self, app):
        from mikiui_app_plugins.api import APIPlugin

        api = APIPlugin()
        app.use(api)

        routes = api.backend_routes()
        assert len(routes) > 0
        paths = [r["path"] for r in routes]
        assert "/openapi.json" in paths
        assert "/docs" in paths


class TestThemeIntegration:
    def test_theme_switching(self, app):
        app.set_theme("dark")
        assert app.theme == "dark"
        app.set_theme("light")
        assert app.theme == "light"


class TestBuildIntegration:
    def test_web_build_produces_output(self, tmp_path):
        app = MikiApp(title="Build Test")

        @app.route("/", methods=("GET",))
        def home():
            return Div("Hello")

        report = build_web(app, mode="fullstack", out_dir=str(tmp_path / "dist"))
        assert report["status"] == "ok"
        assert (tmp_path / "dist" / "index.html").exists()

    def test_desktop_build_produces_launcher(self, tmp_path):
        app = MikiApp(title="Desktop Build Test")

        @app.route("/", methods=("GET",))
        def home():
            return Div("Hello")

        report = build_desktop(app, out_dir=str(tmp_path / "desktop"))
        assert report["status"] == "ok"
        assert (tmp_path / "desktop" / "web").is_dir()
        launcher = tmp_path / "desktop" / ("launch.exe" if __import__("platform").system().lower() == "windows" else "launch")
        assert launcher.exists()


class TestNotificationIntegration:
    def test_notification_plugin(self, app):
        from mikiui_app_plugins.notifications import NotificationPlugin
        from mikiui_app_plugins.session import SessionPlugin

        session = SessionPlugin(secret_key="a-very-long-secret-key-for-testing")
        app.use(session)
        notif = NotificationPlugin()
        app.use(notif)

        token = app.create_session("user1")
        notif.notify("user1", "Hello World", type="success")

        notifications = notif.get_notifications("user1")
        assert len(notifications) == 1
        assert notifications[0]["message"] == "Hello World"
        assert notifications[0]["type"] == "success"

    def test_notification_broadcast(self, app):
        from mikiui_app_plugins.notifications import NotificationPlugin
        from mikiui_app_plugins.session import SessionPlugin

        session = SessionPlugin(secret_key="a-very-long-secret-key-for-testing")
        app.use(session)
        notif = NotificationPlugin()
        app.use(notif)

        notif.broadcast("System update", type="info")

        # Broadcast notifications are stored under the wildcard user "*"
        notifs = notif.get_notifications("*")
        assert len(notifs) == 1
        assert notifs[0]["message"] == "System update"
