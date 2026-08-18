"""Tests for themes, default component styles, and the plugin system."""

from __future__ import annotations

import os
import sys

import pytest

from mikiui import Button, Div, Input, MikiApp, Table, Td, Th, Tr
from mikiui.app.plugins import ComponentPlugin, Plugin, ThemePlugin, WidgetPlugin
from mikiui.engine.renderer import render_page
from mikiui.themes import (
    Theme,
    get_theme,
    list_themes,
    register_theme,
)

# --- Theme registry -----------------------------------------------------------

def test_builtin_themes_exist():
    """All four built-in themes should be registered."""
    names = list_themes()
    assert "light" in names
    assert "dark" in names
    assert "solarized-dark" in names
    assert "dracula" in names


def test_get_theme_returns_theme_object():
    t = get_theme("dark")
    assert t is not None
    assert t.name == "dark"
    assert "background" in t.css().lower() or "--miki-bg" in t.css()


def test_get_theme_unknown_returns_none():
    assert get_theme("nonexistent") is None


def test_register_custom_theme():
    custom = Theme(name="my-custom", source="custom", css_path=None)
    register_theme(custom)
    assert get_theme("my-custom") is custom


def test_theme_css_method_empty_for_no_css_path():
    t = Theme(name="nocss", source="custom", css_path=None)
    assert t.css() == ""


def test_theme_to_dict():
    t = Theme(
        name="test",
        source="plugin",
        extra_classes=["data-theme-test"],
        tailwind_config={"color": "red"},
    )
    d = t.to_dict()
    assert d["name"] == "test"
    assert d["source"] == "plugin"
    assert "data-theme-test" in d["extra_classes"]
    assert d["tailwind_config"]["color"] == "red"


def test_theme_with_framework():
    """Theme can specify a framework (tailwind, bootstrap, css)."""
    t = Theme(
        name="custom-tailwind",
        source="custom",
        framework="tailwind",
        cdn_url="https://example.com/tailwind.css",
        variables={"--miki-bg": "#fff"},
    )
    assert t.framework == "tailwind"
    assert t.cdn_url == "https://example.com/tailwind.css"
    assert t.variables["--miki-bg"] == "#fff"


def test_render_page_with_tailwind_framework():
    """Rendering with Tailwind theme should inject CDN link."""
    page = render_page(Div("test"), title="Test", theme="tailwind")
    assert 'data-miki-theme="tailwind"' in page
    assert "tailwind.min.css" in page or "tailwindcss" in page


# --- MikiApp theme integration ------------------------------------------------

def test_app_default_theme_is_light():
    app = MikiApp()
    assert app.theme == "light"


def test_app_set_theme():
    app = MikiApp()
    app.set_theme("dark")
    assert app.theme == "dark"


def test_app_set_theme_invalid_raises():
    app = MikiApp()
    with pytest.raises(ValueError, match="Unknown theme"):
        app.set_theme("nonexistent")


def test_app_register_theme():
    t = Theme(name="custom-app-theme", source="custom", css_path=None)
    app = MikiApp()
    app.register_theme(t)
    assert app.theme == "custom-app-theme"
    assert get_theme("custom-app-theme") is t


def test_app_theme_config_returns_dict():
    app = MikiApp()
    cfg = app.theme_config()
    assert "name" in cfg
    assert cfg["name"] == "light"


# --- Theme CSS injection in pages ----------------------------------------------

def test_render_page_includes_theme_css():
    app = MikiApp()
    app.set_theme("dark")
    @app.route("/")
    def home():
        return Div("hello")

    page = render_page(Div("hello"), title="Test", theme="dark")
    assert 'data-miki-theme="dark"' in page
    assert "<style id=\"miki-theme\">" in page
    assert "--miki-bg" in page  # theme CSS sets this variable


def test_render_page_default_theme():
    page = render_page(Div("hello"), title="Test")
    assert 'data-miki-theme="light"' in page


# --- Default component classes -------------------------------------------------

def test_button_has_default_classes():
    html = Button("Click").to_html()
    assert "miki-btn" in html
    assert "miki-btn-primary" in html


def test_button_variant_ghost():
    html = Button("Cancel", variant="ghost").to_html()
    assert "miki-btn-ghost" in html
    assert "miki-btn-primary" not in html


def test_button_size_sm():
    html = Button("Go", size="sm").to_html()
    assert "miki-btn-sm" in html


def test_input_has_default_classes():
    html = Input(type="text").to_html()
    assert "miki-input" in html


def test_input_variant_filled():
    html = Input(type="text", variant="filled").to_html()
    assert "miki-input-filled" in html


def test_table_has_default_classes():
    html = Table(Tr(Th("H"), Td("D"))).to_html()
    assert "miki-table" in html
    assert "miki-th" in html
    assert "miki-td" in html


def test_table_striped_variant():
    html = Table(Tr(Th("H"), Td("D")), variant="striped").to_html()
    assert "miki-table-striped" in html


# --- Plugin system -------------------------------------------------------------

def test_plugin_base_class_hooks():
    class MyPlugin(Plugin):
        def __init__(self):
            self.registered = False

        def register(self, app):
            self.registered = True

        def on_render(self, tree):
            tree.append(Div("PLUGIN_MARKER"))
            return tree

    app = MikiApp()
    p = MyPlugin()
    app.use(p)
    assert p.registered is True


def test_theme_plugin_registers_theme():
    class MyThemePlugin(ThemePlugin):
        def theme(self) -> Theme:
            return Theme(name="plugin-theme", source="plugin", css_path=None)

    app = MikiApp()
    plugin = MyThemePlugin()
    app.use(plugin)
    assert get_theme("plugin-theme") is not None


def test_component_plugin_registers_components():
    class MyComp:
        pass

    class MyCompPlugin(ComponentPlugin):
        def components(self) -> dict[str, type]:
            return {"MyComp": MyComp}

    app = MikiApp()
    app.use(MyCompPlugin())
    assert hasattr(app, "_component_registry")
    assert app._component_registry["MyComp"] is MyComp


def test_widget_plugin_registers_widgets():
    class MyWidget:
        pass

    class MyWidgetPlugin(WidgetPlugin):
        def widgets(self) -> dict[str, type]:
            return {"MyWidget": MyWidget}

    app = MikiApp()
    app.use(MyWidgetPlugin())
    assert hasattr(app, "_widget_registry")
    assert app._widget_registry["MyWidget"] is MyWidget


def test_plugin_on_render_modifies_tree():
    class MarkerPlugin(Plugin):
        name = "marker"

        def on_render(self, tree):
            tree.append(Div("INJECTED"))
            return tree

    app = MikiApp()

    @app.route("/")
    def home():
        return Div("original")

    app.use(MarkerPlugin())

    import asyncio

    from mikiui.app.routes import invoke_route

    route = app.get_route("/")
    result, ctx = invoke_route(route, app, None)
    tree, _ctx2 = asyncio.run(app.invoke(route))
    page = render_page(tree, title="Test")
    assert "INJECTED" in page
    assert "original" in page


# --- Tailwind integration ------------------------------------------------------

def test_tailwind_config_generation():
    from mikiui.build.tailwind import tailwind_config

    cfg = tailwind_config(theme="dark", daisyui=True)
    assert "content" in cfg
    assert "theme" in cfg
    assert "plugins" in cfg
    assert "daisyui" in cfg
    assert "mikiui/runtime/miki.css" in cfg["content"]


def test_tailwind_config_without_daisyui():
    from mikiui.build.tailwind import tailwind_config

    cfg = tailwind_config(theme="light", daisyui=False)
    assert "daisyui" not in cfg


def test_daisyui_config_bridges_theme():
    from mikiui.build.tailwind import daisyui_config

    dcfg = daisyui_config("dark")
    assert "mikiui-dark" in dcfg
    theme_vars = dcfg["mikiui-dark"]
    assert len(theme_vars) > 0


def test_component_library_link():
    from mikiui.build.tailwind import component_library_link

    link = component_library_link("daisyui")
    assert "daisyui" in link.lower()
    assert "<script" in link
    assert component_library_link("nonexistent") == ""


# --- Per-page title ------------------------------------------------------------

def test_route_decorator_accepts_title():
    """The @app.route decorator should accept a title parameter."""
    app = MikiApp(title="Default")

    @app.route("/page", title="Custom Page Title")
    def page():
        return Div("content")

    route = app.get_route("/page")
    assert route.title == "Custom Page Title"


def test_route_title_defaults_to_none():
    """Routes without a title should have title=None."""
    app = MikiApp()

    @app.route("/no-title")
    def page():
        return Div("content")

    route = app.get_route("/no-title")
    assert route.title is None


def test_resolve_title_fallback_to_app_title():
    """resolve_title should fall back to the app's global title."""
    from mikiui.app.routes import resolve_title

    app = MikiApp(title="Global Title")

    @app.route("/")
    def home():
        return Div("hi")

    route = app.get_route("/")
    assert resolve_title(route, None, app.title) == "Global Title"


def test_resolve_title_uses_route_title():
    """resolve_title should prefer route.title over the app title."""
    from mikiui.app.routes import resolve_title

    app = MikiApp(title="Global")

    @app.route("/", title="Route Title")
    def home():
        return Div("hi")

    route = app.get_route("/")
    assert resolve_title(route, None, app.title) == "Route Title"


def test_resolve_title_uses_ctx_meta():
    """resolve_title should prefer ctx.meta['title'] over route.title."""
    from mikiui.app.routes import invoke_route, resolve_title

    app = MikiApp(title="Global")

    @app.route("/", title="Route Title")
    def home(ctx):
        ctx.meta["title"] = "Meta Title"
        return Div("hi")

    route = app.get_route("/")
    result, ctx = invoke_route(route, app, None)
    assert ctx is not None
    assert ctx.meta["title"] == "Meta Title"
    assert resolve_title(route, ctx, app.title) == "Meta Title"


def test_server_uses_per_page_title():
    """The backend should render the per-page title in the <title> tag."""
    from fastapi.testclient import TestClient

    from mikiui.backend import create_app

    app = MikiApp(title="Global Title")

    @app.route("/", title="Home Page")
    def home():
        return Div("home")

    @app.route("/about", title="About Us")
    def about():
        return Div("about")

    client = TestClient(create_app(app))
    assert "<title>Home Page</title>" in client.get("/").text
    assert "<title>About Us</title>" in client.get("/about").text


# --- App discovery -------------------------------------------------------------

def test_resolve_app_spec_with_explicit_spec():
    """resolve_app_spec should accept an explicit module:attr spec."""
    from mikiui.cli.app_discovery import resolve_app_spec

    spec = resolve_app_spec("mikiui.examples.demo1:app")
    assert spec == "mikiui.examples.demo1:app"


def test_resolve_app_spec_appends_attr():
    """resolve_app_spec should append ':app' if no attr is given."""
    from mikiui.cli.app_discovery import resolve_app_spec

    spec = resolve_app_spec("mikiui.examples.demo1")
    assert spec == "mikiui.examples.demo1:app"


def test_discover_app_finds_module(tmp_path):
    """discover_app should find app.py in the current directory."""
    import os
    import sys

    test_app_content = '''
from mikiui import MikiApp
app = MikiApp(title="Test Discovered")
'''
    app_file = tmp_path / "app.py"
    app_file.write_text(test_app_content)

    original_cwd = os.getcwd()
    original_sys = sys.path[:]
    try:
        os.chdir(tmp_path)
        sys.path.insert(0, str(tmp_path))
        from mikiui.cli.app_discovery import discover_app

        spec = discover_app()
        assert spec is not None
        assert "app:app" in spec
    finally:
        os.chdir(original_cwd)
        sys.path[:] = original_sys
        # Clean up sys.modules
        sys.modules.pop("app", None)


def test_discover_app_returns_none_without_mikiapp(tmp_path):
    """discover_app should return None if no MikiApp is found."""
    test_content = '''
x = 42
def hello(): pass
'''
    (tmp_path / "app.py").write_text(test_content)
    (tmp_path / "main.py").write_text(test_content)

    original_cwd = os.getcwd()
    original_sys = sys.path[:]
    try:
        os.chdir(tmp_path)
        sys.path.insert(0, str(tmp_path))
        from mikiui.cli.app_discovery import discover_app

        assert discover_app() is None
    finally:
        os.chdir(original_cwd)
        sys.path[:] = original_sys
        sys.modules.pop("app", None)
        sys.modules.pop("main", None)


def test_cli_dev_auto_discovers_app(tmp_path):
    """`mikiui dev` without --app should auto-discover app.py."""
    pytest.importorskip("typer.testing")
    from unittest import mock

    from typer.testing import CliRunner

    from mikiui.cli import cli

    runner = CliRunner()
    with mock.patch("mikiui.cli.commands.resolve_app_spec") as resolve:
        resolve.return_value = "mikiui.examples.demo1:app"
        with mock.patch("uvicorn.run"):
            result = runner.invoke(cli, ["dev", "--no-reload", "--port", "9999"])
            assert result.exit_code == 0, result.stdout
            resolve.assert_called_once()


def test_resolve_app_spec_raises_without_app(tmp_path):
    """resolve_app_spec should raise AppDiscoveryError when no app is found."""
    original_cwd = os.getcwd()
    original_sys = sys.path[:]
    try:
        os.chdir(tmp_path)
        sys.path.insert(0, str(tmp_path))
        from mikiui.cli.app_discovery import AppDiscoveryError, resolve_app_spec

        # No .py files with MikiApp in the temp dir
        (tmp_path / "empty.py").write_text("x = 42\n")
        with pytest.raises(AppDiscoveryError, match="No MikiApp instance found"):
            resolve_app_spec(None)
    finally:
        os.chdir(original_cwd)
        sys.path[:] = original_sys
        sys.modules.pop("empty", None)


def test_discover_app_finds_miki_app_via_ast(tmp_path):
    """discover_app should find MikiApp via AST scan without importing."""
    test_content = '''
from mikiui import MikiApp
app = MikiApp(title="Test")
'''
    (tmp_path / "myapp.py").write_text(test_content)

    original_cwd = os.getcwd()
    original_sys = sys.path[:]
    try:
        os.chdir(tmp_path)
        sys.path.insert(0, str(tmp_path))
        from mikiui.cli.app_discovery import discover_app

        spec = discover_app()
        assert spec == "myapp:app"
    finally:
        os.chdir(original_cwd)
        sys.path[:] = original_sys
        sys.modules.pop("myapp", None)


def test_cli_desktop_auto_discovers_app(tmp_path):
    pytest.importorskip("typer.testing")
    from unittest import mock

    from typer.testing import CliRunner

    from mikiui.cli import cli
    from mikiui.cli import commands as cmd_mod

    runner = CliRunner()
    fake_app = MikiApp(title="Theme Desktop Test")

    import mikiui.app.app as app_module

    original_app = getattr(app_module, "app", None)
    app_module.app = fake_app
    try:
        with mock.patch.object(cmd_mod, "_safe_resolve", return_value="mikiui.app.app:app"), mock.patch(
            "mikiui.build.run_desktop"
        ) as mocked:
            result = runner.invoke(cli, ["desktop", "--browser"])
            assert result.exit_code == 0, result.stdout
            mocked.assert_called_once()
    finally:
        if original_app is None:
            delattr(app_module, "app")
        else:
            app_module.app = original_app
