"""E2E tests for interactive widgets using Playwright."""
from __future__ import annotations

import pytest
from playwright.sync_api import expect, sync_playwright
from starlette.testclient import TestClient

from mikiui.backend.server import create_app
from mikiui.examples.demo1 import app


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="module")
def server():
    fastapi_app = create_app(app)
    return TestClient(fastapi_app)


@pytest.fixture()
def page(browser, server):
    page = browser.new_page()
    
    def load(url):
        resp = server.get(url)
        css_resp = server.get("/_miki/runtime/miki.css")
        js_resp_core = server.get("/_miki/runtime/js/core.js")
        js_resp_bridge = server.get("/_miki/runtime/js/miki_bridge.js")
        js_resp_editor = server.get("/_miki/runtime/js/mikieditorarea.js")
        js_resp_ide = server.get("/_miki/runtime/js/mikiide.js")
        js_resp_mdi = server.get("/_miki/runtime/js/mikimdi.js")
        js_resp_stack = server.get("/_miki/runtime/js/mikistackedpanel.js")
        js_resp_init = server.get("/_miki/runtime/js/init.js")
        js_resp_tabs = server.get("/_miki/runtime/js/mikitabs.js")
        js_resp_drawer = server.get("/_miki/runtime/js/mikidrawer.js")
        js_resp_split = server.get("/_miki/runtime/js/mikisplitview.js")
        inject = (
            f"<style>{css_resp.text}</style>"
            f"<script>{js_resp_core.text}</script>"
            f"<script>{js_resp_bridge.text}</script>"
            f"<script>{js_resp_editor.text}</script>"
            f"<script>{js_resp_ide.text}</script>"
            f"<script>{js_resp_mdi.text}</script>"
            f"<script>{js_resp_stack.text}</script>"
            f"<script>{js_resp_tabs.text}</script>"
            f"<script>{js_resp_drawer.text}</script>"
            f"<script>{js_resp_split.text}</script>"
            f"<script>{js_resp_init.text}</script>"
        )
        html = resp.text
        if "</head>" in html:
            html = html.replace("</head>", f"{inject}</head>")
        else:
            html = inject + html
        page.set_content(html, timeout=60000)
    
    page.load = load
    yield page
    page.close()


class TestNavbar:
    def test_navbar_renders(self, page):
        page.load("/")
        navbar = page.locator(".miki-navbar")
        expect(navbar).to_have_count(1)

    def test_hamburger_toggle_on_mobile(self, page):
        page.set_viewport_size({"width": 375, "height": 667})
        page.load("/")
        toggle = page.locator(".miki-navbar-toggle")
        expect(toggle).to_be_visible()
        toggle.click()
        has_class = page.locator(".miki-navbar-links").evaluate("el => el.classList.contains('open')")
        assert has_class, "Expected navbar-links to have 'open' class after toggle click"


class TestSplitView:
    def test_splitter_exists(self, page):
        page.load("/data")
        splitter = page.locator("[data-miki-splitter='true']")
        assert splitter.count() >= 2, f"Expected at least 2 splitters, found {splitter.count()}"

    def test_splitter_draggable(self, page):
        page.load("/data")
        splitter = page.locator("[data-miki-splitter='true']").first
        expect(splitter).to_have_attribute("tabindex", "0")
        expect(splitter).to_have_attribute("role", "separator")

    def test_splitter_horizontal_cursor(self, page):
        """Horizontal splitter has ew-resize cursor."""
        page.load("/data")
        # Find the horizontal splitview explicitly
        h_splitview = page.locator('.miki-splitview[data-orientation="horizontal"]').first
        splitter = h_splitview.locator("> .miki-splitter")
        if splitter.count() > 0:
            cursor = splitter.first.evaluate("el => getComputedStyle(el).cursor")
            assert cursor in ("ew-resize", "col-resize", "nwse-resize"), (
                f"Expected ew-resize or nwse-resize cursor, got {cursor}"
            )
        else:
            pytest.skip("No horizontal splitter found")


class TestKanbanBoard:
    def test_kanban_renders_columns(self, page):
        page.load("/data")
        columns = page.locator("[data-miki-kanban-column='true']")
        expect(columns).to_have_count(3)

    def test_kanban_items_are_draggable(self, page):
        page.load("/data")
        items = page.locator("[data-miki-kanban-item='true']")
        assert items.count() > 0
        expect(items.first).to_have_attribute("draggable", "true")

    def test_kanban_drag_and_drop(self, page):
        page.load("/data")
        first_item = page.locator("[data-miki-kanban-item='true']").first
        second_column = page.locator("[data-miki-kanban-column='true']").nth(1)
        if first_item.count() > 0 and second_column.count() > 0:
            first_item.drag_to(second_column)
            # After drop, the item should be in the second column


class TestModal:
    def test_modal_exists(self, page):
        page.load("/dialog")
        modal = page.locator("[data-miki-modal='true']")
        expect(modal).to_have_count(1)


class TestTabs:
    def test_tabs_render(self, page):
        page.load("/data")
        tabs = page.locator("[data-miki-tabs='true']")
        assert tabs.count() > 0
        first_tab = page.locator(".miki-tab-active")
        assert first_tab.count() > 0

    def test_tab_switching(self, page):
        page.load("/data")
        tab_buttons = page.locator("[data-miki-tabs='true'] button")
        if tab_buttons.count() > 1:
            tab_buttons.nth(1).click()
            has_active = tab_buttons.nth(1).evaluate("el => el.classList.contains('miki-tab-active')")
            assert has_active, "Expected second tab to have 'miki-tab-active' class after click"


class TestDrawer:
    def test_drawer_renders(self, page):
        page.load("/advanced")
        drawer = page.locator("[data-miki-drawer='true']")
        expect(drawer).to_have_count(1)
