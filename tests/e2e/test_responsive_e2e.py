"""E2E tests for responsive layout and mobile behavior.

Run with:  pytest tests/e2e/test_responsive_e2e.py -v
"""
from __future__ import annotations

import re

import pytest
from playwright.sync_api import expect, sync_playwright
from starlette.testclient import TestClient

from mikiui.backend.server import create_app
from mikiui.examples.kitchen_sink import app


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="module")
def server():
    fastapi_app = create_app(app, enable_csrf=False)
    return TestClient(fastapi_app)


def _load_js(server):
    """Load all widget JS modules concatenated into a single string."""
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
        "mikiscrollview.js", "init.js",
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
    # Remove external CDN links that would fail in test
    html = re.sub(r'<script src="https://cdn\.tailwindcss\.com"></script>', '', html)
    html = re.sub(r'<link rel="stylesheet" href="https://cdn\.jsdelivr\.net[^"]*">', '', html)
    return html


class TestMobileViewport:
    """Test that the app renders correctly on mobile viewports."""

    def test_iphone_se_layout(self, browser, server):
        """Page renders without horizontal overflow on iPhone SE (375x667)."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        # Check no horizontal overflow
        overflow = page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
        assert overflow, "Page has horizontal overflow on iPhone SE viewport"

        context.close()

    def test_iphone_14_layout(self, browser, server):
        """Page renders without horizontal overflow on iPhone 14 (390x844)."""
        context = browser.new_context(viewport={"width": 390, "height": 844})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        overflow = page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
        assert overflow, "Page has horizontal overflow on iPhone 14 viewport"

        context.close()

    def test_ipad_layout(self, browser, server):
        """Page renders without horizontal overflow on iPad (768x1024)."""
        context = browser.new_context(viewport={"width": 768, "height": 1024})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        overflow = page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
        assert overflow, "Page has horizontal overflow on iPad viewport"

        context.close()

    def test_pixel_7_layout(self, browser, server):
        """Page renders without horizontal overflow on Pixel 7 (412x915)."""
        context = browser.new_context(viewport={"width": 412, "height": 915})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        overflow = page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")
        assert overflow, "Page has horizontal overflow on Pixel 7 viewport"

        context.close()


class TestTouchInteractions:
    """Test that interactive elements work with touch events."""

    def test_button_tap(self, browser, server):
        """Buttons respond to tap events on touch devices."""
        context = browser.new_context(
            viewport={"width": 375, "height": 667},
            has_touch=True,
        )
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        # Find a button and tap it
        buttons = page.locator(".miki-btn, button")
        if buttons.count() > 0:
            first_button = buttons.first
            first_button.tap()
            page.wait_for_timeout(200)
            # No crash = success

        context.close()

    def test_menu_tap(self, browser, server):
        """Menu bar items respond to tap on touch devices."""
        context = browser.new_context(
            viewport={"width": 375, "height": 667},
            has_touch=True,
        )
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        # Find menu titles and tap
        menu_titles = page.locator(".miki-menu-title")
        if menu_titles.count() > 0:
            menu_titles.first.tap()
            page.wait_for_timeout(300)
            # Check dropdown appeared
            dropdowns = page.locator(".miki-menu-dropdown")
            if dropdowns.count() > 0:
                expect(dropdowns.first).to_be_visible()

        context.close()

    def test_tab_tap(self, browser, server):
        """Tabs respond to tap on touch devices."""
        context = browser.new_context(
            viewport={"width": 375, "height": 667},
            has_touch=True,
        )
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        tabs = page.locator("[role='tab']")
        if tabs.count() > 1:
            tabs.nth(1).tap()
            page.wait_for_timeout(200)
            # Check second tab is now active
            second_tab = tabs.nth(1)
            expect(second_tab).to_have_attribute("aria-selected", "true")

        context.close()


class TestResponsiveWidgets:
    """Test that widgets adapt to mobile viewports."""

    def test_chat_mobile_height(self, browser, server):
        """Chat widget uses full viewport height on mobile."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        chat = page.locator(".miki-chat")
        if chat.count() > 0:
            box = chat.first.bounding_box()
            assert box is not None
            # On mobile, chat should be tall (full viewport or close)
            assert box["height"] >= 500, f"Chat height {box['height']} too small on mobile"

        context.close()

    def test_editor_mobile_layout(self, browser, server):
        """Editor adapts to mobile viewport width."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        editor = page.locator(".miki-ide")
        if editor.count() > 0:
            box = editor.first.bounding_box()
            assert box is not None
            # Editor should not overflow viewport width
            assert box["width"] <= 375, f"Editor width {box['width']} exceeds viewport"

        context.close()

    def test_mdi_window_mobile(self, browser, server):
        """MDI sub-windows go fullscreen on mobile."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        windows = page.locator(".miki-mdi-subwindow")
        if windows.count() > 0:
            box = windows.first.bounding_box()
            assert box is not None
            # On mobile, windows should be fullscreen (or close to it)
            assert box["width"] >= 350, f"MDI window width {box['width']} not fullscreen on mobile"

        context.close()


class TestOrientationChange:
    """Test that layout adapts to orientation changes."""

    def test_portrait_to_landscape(self, browser, server):
        """Layout adapts when rotating from portrait to landscape."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(300)

        # Check portrait
        overflow_portrait = page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")

        # Rotate to landscape
        page.set_viewport_size({"width": 667, "height": 375})
        page.wait_for_timeout(300)

        overflow_landscape = page.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth")

        assert overflow_portrait, "Overflow in portrait mode"
        assert overflow_landscape, "Overflow in landscape mode"

        context.close()


class TestAccessibilityMobile:
    """Test accessibility features work on mobile."""

    def test_focus_visible_on_mobile(self, browser, server):
        """Focus indicators are visible on mobile (for keyboard accessibility)."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        # Tab to first focusable element
        page.keyboard.press("Tab")
        page.wait_for_timeout(200)

        # Check that a focused element exists
        focused = page.evaluate("() => document.activeElement !== document.body")
        assert focused, "No element received focus after Tab"

        context.close()

    def test_dialog_focus_trap_mobile(self, browser, server):
        """Dialogs trap focus correctly on mobile."""
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        html = _load_page(server, "/")
        page.set_content(html, timeout=60000)
        page.wait_for_timeout(500)

        # Check for dialog elements
        dialogs = page.locator(".miki-dialog, .miki-modal, [role='dialog']")
        if dialogs.count() > 0:
            dialog = dialogs.first
            if dialog.is_visible():
                # Tab within dialog should keep focus inside
                page.keyboard.press("Tab")
                page.wait_for_timeout(200)
                # Focus should be within the dialog
                in_dialog = page.evaluate("""() => {
                    const dialog = document.querySelector('.miki-dialog, .miki-modal, [role="dialog"]');
                    return dialog && dialog.contains(document.activeElement);
                }""")
                assert in_dialog, "Focus escaped dialog on mobile"

        context.close()
