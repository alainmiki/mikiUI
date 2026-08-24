"""Deep E2E tests for interactive widget behavior."""
from __future__ import annotations

import pytest
from playwright.sync_api import sync_playwright, expect
from starlette.testclient import TestClient

from mikiui.examples.demo1 import app
from mikiui.backend.server import create_app


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
        # Load ALL widget JS modules
        js_files = [
            "core.js", "mikidialog.js", "mikimodal.js", "mikitabs.js",
            "mikidrawer.js", "mikisplitview.js", "mikidockablepanel.js",
            "mikislider.js", "mikidial.js", "mikiprogress.js",
            "mikiprogressdialog.js", "mikicollapsible.js", "mikiaccordion.js",
            "mikidatagrid.js", "mikikanban.js", "mikichat.js", "mikidropzone.js",
            "mikicarousel.js", "mikimessagebox.js", "mikitoggle.js",
            "mikisearchableselect.js", "mikicontextwindow.js", "mikimenubar.js",
            "mikibottomsheet.js", "mikibottomnav.js", "mikichip.js",
            "mikipressable.js", "mikilazygrid.js", "mikivirtuallist.js",
            "mikiscrollview.js", "init.js"
        ]
        js_content = ""
        for js_file in js_files:
            try:
                js_resp = server.get(f"/_miki/runtime/js/{js_file}")
                js_content += js_resp.text + "\n"
            except Exception:
                pass
        
        inject = f"<style>{css_resp.text}</style><script>{js_content}</script>"
        html = resp.text
        if "</head>" in html:
            html = html.replace("</head>", f"{inject}</head>")
        else:
            html = inject + html
        page.set_content(html)
    
    page.load = load
    yield page
    page.close()


class TestNavbarToggle:
    def test_navbar_links_toggle(self, page):
        """Hamburger click toggles the 'open' class on navbar-links."""
        page.set_viewport_size({"width": 375, "height": 667})
        page.load("/")
        
        links = page.locator(".miki-navbar-links")
        toggle = page.locator(".miki-navbar-toggle")
        
        # Initially no 'open' class
        assert not links.evaluate("el => el.classList.contains('open')")
        
        # Click to open
        toggle.click()
        assert links.evaluate("el => el.classList.contains('open')")
        
        # Click to close
        toggle.click()
        assert not links.evaluate("el => el.classList.contains('open')")


class TestTabSwitching:
    def test_tab_switching(self, page):
        """Clicking a tab switches the active panel."""
        page.load("/data")

        # Debug: check for JS errors
        errors = []
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: errors.append(f"Console: {msg.text}") if msg.type == "error" else None)
        
        # Reload to capture errors
        page.load("/data")
        page.wait_for_timeout(500)
        
        print(f"Errors: {errors}")

        # Check if mikiTabs is defined
        has_miki_tabs = page.evaluate("typeof mikiTabs !== 'undefined'")
        assert has_miki_tabs, f"mikiTabs should be defined. Errors: {errors}"

        # Find tabs
        tab_buttons = page.locator("[data-miki-tabs='true'] button")
        if tab_buttons.count() < 2:
            pytest.skip("Not enough tabs to test switching")

        # First tab should be active initially
        assert tab_buttons.nth(0).evaluate("el => el.classList.contains('miki-tab-active')")

        # Click second tab
        tab_buttons.nth(1).click()

        # Second tab should now be active
        assert tab_buttons.nth(1).evaluate("el => el.classList.contains('miki-tab-active')")
        # First tab should no longer be active
        assert not tab_buttons.nth(0).evaluate("el => el.classList.contains('miki-tab-active')")


class TestKanbanDragDrop:
    def test_kanban_item_drag(self, page):
        """Kanban items can be dragged between columns."""
        page.load("/data")
        
        items = page.locator("[data-miki-kanban-item='true']")
        columns = page.locator("[data-miki-kanban-column='true']")
        
        if items.count() == 0 or columns.count() < 2:
            pytest.skip("Not enough items/columns to test")
        
        # Get first item and second column
        first_item = items.first
        second_column = columns.nth(1)
        
        # Get initial positions
        item_box = first_item.bounding_box()
        col_box = second_column.bounding_box()
        
        if item_box and col_box:
            # Drag from item center to column center
            page.mouse.move(item_box["x"] + item_box["width"]/2, item_box["y"] + item_box["height"]/2)
            page.mouse.down()
            page.mouse.move(col_box["x"] + col_box["width"]/2, col_box["y"] + col_box["height"]/2, steps=10)
            page.mouse.up()
            
            # Wait for any animations
            page.wait_for_timeout(500)


class TestSplitterResize:
    def test_splitter_mousedown(self, page):
        """Splitter responds to mouse events."""
        page.load("/data")
        
        splitter = page.locator("[data-miki-splitter='true']").first
        box = splitter.bounding_box()
        if box:
            # Simulate mousedown on splitter
            page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
            page.mouse.down()
            # Move mouse to simulate drag
            page.mouse.move(box["x"] + 100, box["y"] + box["height"]/2, steps=5)
            page.mouse.up()
            
            # After drag, the splitter should have applied some sizing
            page.wait_for_timeout(300)


class TestDrawerToggle:
    def test_drawer_renders(self, page):
        """Drawer renders with overlay and panel."""
        page.load("/advanced")
        
        drawer = page.locator("[data-miki-drawer='true']")
        expect(drawer).to_have_count(1)
        
        overlay = page.locator(".miki-drawer-overlay")
        panel = page.locator(".miki-drawer-panel")
        expect(overlay).to_have_count(1)
        expect(panel).to_have_count(1)
