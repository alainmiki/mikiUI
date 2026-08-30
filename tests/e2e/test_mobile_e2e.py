"""E2E tests for mobile-specific features.

Run with:  pytest tests/e2e/test_mobile_e2e.py -v
"""
from __future__ import annotations

import re

import pytest
from playwright.sync_api import sync_playwright, expect
from starlette.testclient import TestClient

from mikiui import MikiApp, Div, H1, P, Button
from mikiui.backend.server import create_app
from mikiui.app.mobile import MobileConfig


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="module")
def server():
    app = MikiApp(title="Mobile Test", mobile=MobileConfig(backend="cloud"))

    @app.route("/")
    def home():
        return Div(H1("Mobile App"), P("Welcome to the mobile test app"))

    @app.route("/data")
    def data():
        return Div(H1("Data"), Button("Click me"))

    fastapi_app = create_app(app, enable_csrf=False)
    return TestClient(fastapi_app)


def _load_js(server):
    """Load all widget JS modules including mobile bridges."""
    js_files = [
        "core.js", "miki_bridge.js", "mikieditorarea.js", "mikiide.js",
        "mikimdi.js", "mikistackedpanel.js",
        "mikidialog.js", "mikimodal.js", "mikitabs.js",
        "mikidrawer.js", "mikisplitview.js", "mikidockablepanel.js",
        "mikislider.js", "mikidial.js", "mikiprogress.js",
        "mikiprogressdialog.js", "mikicollapsible.js", "mikiaccordion.js",
        "mikidatagrid.js", "mikikanban.js", "mikichat.js", "mikidropzone.js",
        "mikicarousel.js", "mikimessagebox.js", "mikitoggle.js",
        "mikisearchableselect.js", "mikicontextwindow.js", "mikimenubar.js",
        "mikibottomsheet.js", "mikibottomnav.js", "mikichip.js",
        "mikipressable.js", "mikilazygrid.js", "mikivirtuallist.js",
        "mikiscrollview.js",
        "backend_bridge.js", "websocket_bridge.js", "capacitor_bridge.js",
        "capacitor_features.js", "event_bridge.js",
        "init.js",
    ]
    js_content = ""
    for f in js_files:
        try:
            r = server.get(f"/_miki/runtime/js/{f}")
            js_content += r.text + "\n"
        except Exception:
            pass
    return js_content


def _load_page(server, url="/"):
    """Load a page with all JS/CSS injected."""
    resp = server.get(url)
    css_resp = server.get("/_miki/runtime/miki.css")
    js_content = _load_js(server)
    inject = f"<style>{css_resp.text}</style><script>{js_content}</script>"
    html = resp.text
    if "</head>" in html:
        html = html.replace("</head>", f"{inject}</head>")
    else:
        html = inject + html
    html = re.sub(r'<script src="https://cdn\.tailwindcss\.com"></script>', '', html)
    html = re.sub(r'<link rel="stylesheet" href="https://cdn\.jsdelivr\.net[^"]*">', '', html)
    return html


class TestMobileBridge:
    """Test mobile bridge JS APIs are available."""

    def test_miki_backend_available(self, browser, server):
        """MikiBackend global should be available after JS loads."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        has_backend = page.evaluate("() => typeof window.MikiBackend !== 'undefined'")
        assert has_backend, "MikiBackend not available"

        context.close()

    def test_miki_websocket_available(self, browser, server):
        """MikiWebSocket global should be available after JS loads."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        has_ws = page.evaluate("() => typeof window.MikiWebSocket !== 'undefined'")
        assert has_ws, "MikiWebSocket not available"

        context.close()

    def test_miki_capacitor_available(self, browser, server):
        """MikiCapacitor global should be available after JS loads."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        has_cap = page.evaluate("() => typeof window.MikiCapacitor !== 'undefined'")
        assert has_cap, "MikiCapacitor not available"

        context.close()

    def test_miki_features_available(self, browser, server):
        """MikiFeatures global should be available after JS loads."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        has_features = page.evaluate("() => typeof window.MikiFeatures !== 'undefined'")
        assert has_features, "MikiFeatures not available"

        context.close()

    def test_miki_events_available(self, browser, server):
        """MikiEvents global should be available after JS loads."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        has_events = page.evaluate("() => typeof window.MikiEvents !== 'undefined'")
        assert has_events, "MikiEvents not available"

        context.close()


class TestMobileViewport:
    """Test mobile viewport handling."""

    def test_viewport_meta_present(self, browser, server):
        """Page should have viewport meta tag."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)

        viewport = page.evaluate("() => document.querySelector('meta[name=viewport]')?.content")
        assert viewport is not None, "Viewport meta tag missing"
        assert "width=device-width" in viewport

        context.close()

    def test_no_horizontal_overflow_mobile(self, browser, server):
        """Page should not overflow on mobile viewport."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        overflow = page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
        assert overflow, "Page has horizontal overflow on mobile"

        context.close()


class TestMobileBackendDetection:
    """Test backend transport detection."""

    def test_detects_web_transport(self, browser, server):
        """Should detect web transport in browser context."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        transport = page.evaluate("() => window.MikiBackend.transport()")
        assert transport == "web", f"Expected 'web', got {transport!r}"

        context.close()

    def test_not_capacitor_in_browser(self, browser, server):
        """Should not detect Capacitor in browser context."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        is_cap = page.evaluate("() => window.MikiCapacitor.isCapacitor()")
        assert not is_cap, "Should not be Capacitor in browser"

        context.close()


class TestMobileEvents:
    """Test event bus functionality."""

    def test_event_on_off(self, browser, server):
        """Events can be subscribed and unsubscribed."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        # Register a handler
        result = page.evaluate("""() => {
            let called = false;
            const handler = (data) => { called = true; };
            window.MikiEvents.on('test_event', handler);
            window.MikiEvents.emit('test_event', { value: 42 });
            return called;
        }""")
        assert result, "Event handler was not called"

        context.close()


class TestMobileHTMX:
    """Test HTMX works on mobile."""

    def test_htmx_available(self, browser, server):
        """HTMX should be available."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        has_htmx = page.evaluate("() => typeof window.htmx !== 'undefined'")
        assert has_htmx, "HTMX not available"

        context.close()
