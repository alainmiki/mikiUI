"""Tests for ThemeSwitcher widget."""
from __future__ import annotations

from mikiui import Div, MikiApp
from mikiui.widgets.theme_switcher import ThemeSwitcher


def _make_app(theme: str = "light"):
    app = MikiApp(title="Test")
    app.set_theme(theme)
    return app


class TestThemeSwitcherDefaults:
    def test_renders_select_with_all_themes(self):
        app = _make_app("dark")
        widget = ThemeSwitcher(app)
        html = widget.to_html()
        assert '<select' in html
        assert 'value="light"' in html
        assert 'value="dark"' in html
        assert 'value="dracula"' in html
        assert 'value="solarized-dark"' in html

    def test_current_theme_is_selected(self):
        app = _make_app("dracula")
        widget = ThemeSwitcher(app)
        html = widget.to_html()
        assert 'value="dracula"' in html
        assert 'selected' in html

    def test_has_label(self):
        app = _make_app()
        widget = ThemeSwitcher(app, label="Choose Theme")
        html = widget.to_html()
        assert "Choose Theme" in html
        assert 'id="miki-theme-switcher-label"' in html

    def test_aria_attributes(self):
        app = _make_app()
        widget = ThemeSwitcher(app)
        html = widget.to_html()
        assert 'role="group"' in html
        assert 'aria-label="Theme Switcher"' in html
        assert 'aria-labelledby="miki-theme-switcher-label"' in html

    def test_has_css_classes(self):
        app = _make_app()
        widget = ThemeSwitcher(app)
        html = widget.to_html()
        assert "miki-theme-switcher" in html
        assert "miki-theme-select" in html

    def test_option_values(self):
        app = _make_app()
        widget = ThemeSwitcher(app, themes=["light", "dark", "dracula"])
        html = widget.to_html()
        assert 'value="light"' in html
        assert 'value="dark"' in html
        assert 'value="dracula"' in html
        assert 'value="solarized-dark"' not in html

    def test_disabled(self):
        app = _make_app()
        widget = ThemeSwitcher(app, disabled=True)
        html = widget.to_html()
        assert "disabled" in html
        assert 'aria-disabled="true"' in html

    def test_htmx_get_adds_attributes(self):
        app = _make_app()
        widget = ThemeSwitcher(app, htmx_get="/set-theme")
        html = widget.to_html()
        assert 'hx-get="/set-theme"' in html
        assert 'hx-trigger="change"' in html
        assert 'hx-swap="none"' in html
        assert 'hx-refresh="true"' in html

    def test_custom_placeholder(self):
        app = _make_app()
        widget = ThemeSwitcher(app, placeholder="Pick a theme...")
        html = widget.to_html()
        assert 'data-placeholder="Pick a theme..."' in html


class TestThemeSwitcherCustomThemes:
    def test_custom_theme_list(self):
        app = _make_app()
        widget = ThemeSwitcher(app, themes=["my-theme-1", "my-theme-2"])
        html = widget.to_html()
        assert 'value="my-theme-1"' in html
        assert 'value="my-theme-2"' in html
        assert 'value="light"' not in html

    def test_empty_themes_list(self):
        app = _make_app()
        widget = ThemeSwitcher(app, themes=[])
        html = widget.to_html()
        assert '<select' in html


class TestThemeSwitcherIntegration:
    def test_render_page_contains_switcher(self):
        app = _make_app("dark")

        @app.route("/")
        def home():
            return Div(ThemeSwitcher(app))

        from starlette.testclient import TestClient

        from mikiui.backend.server import create_app

        client = TestClient(create_app(app))
        resp = client.get("/")
        assert resp.status_code == 200
        assert "miki-theme-switcher" in resp.text
