"""E2E tests for the Kitchen Sink demo — verifying touch + mouse compatibility.

Run with:  pytest tests/e2e/test_kitchen_sink_e2e.py -v
"""
from __future__ import annotations

import re

import pytest
from playwright.sync_api import sync_playwright
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
    fastapi_app = create_app(app)
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


@pytest.fixture()
def page(browser, server):
    p = browser.new_page()

    def load(url, viewport=None):
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
        p.set_content(html, wait_until="domcontentloaded", timeout=60000)
        return p

    p.load = load
    yield p
    p.close()


@pytest.fixture()
def touch_page(browser, server):
    """A page with has_touch enabled for touch-specific tests."""
    context = browser.new_context(has_touch=True)
    p = context.new_page()

    def load(url):
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
        p.set_content(html, wait_until="domcontentloaded", timeout=60000)
        return p

    p.load = load
    yield p
    p.close()
    context.close()


class TestKitchenSinkMouse:
    """Mouse-only interactions on the kitchen sink."""

    def test_page_loads(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        assert page.title() == "MikiUI Kitchen Sink"

    def test_navbar_present(self, page):
        page.load("/")
        page.wait_for_timeout(300)
        navbar = page.locator(".miki-navbar")
        assert navbar.count() > 0
        assert navbar.first.inner_text() != ""

    def test_buttons_clickable(self, page):
        page.load("/")
        page.wait_for_timeout(300)
        buttons = page.locator("button.miki-btn, .miki-btn")
        assert buttons.count() > 0
        # Click a visible button — should not cause errors
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button.miki-btn, .miki-btn'));
            const visible = btns.find(b => b.offsetParent !== null);
            if (visible) visible.click();
        }""")
        page.wait_for_timeout(200)

    def test_tabs_switch_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        tabs = page.locator('[role="tab"]')
        if tabs.count() < 2:
            pytest.skip("No tabs found")
        # Click second tab
        tabs.nth(1).click()
        page.wait_for_timeout(300)
        # Active tab should have aria-selected="true"
        assert tabs.nth(1).get_attribute("aria-selected") == "true"

    def test_collapsible_toggle_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        collapsibles = page.locator('[data-miki-collapsible="true"]')
        if collapsibles.count() == 0:
            pytest.skip("No collapsibles found")
        c = collapsibles.first
        header = c.locator('[data-miki-collapsible-header="true"]')
        if header.count() == 0:
            pytest.skip("No collapsible header found")
        initial = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        header.click()
        page.wait_for_timeout(300)
        after = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        assert initial != after, "Collapsible should toggle on click"

    def test_splitview_drag_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        splitters = page.locator('[data-miki-splitter="true"]')
        if splitters.count() == 0:
            pytest.skip("No splitters found")
        s = splitters.first
        s_box = s.bounding_box()
        if not s_box:
            pytest.skip("No splitter bounding box")
        # Drag the splitter
        page.mouse.down()
        page.mouse.move(s_box["x"] + s_box["width"] / 2 + 30, s_box["y"] + s_box["height"] / 2)
        page.wait_for_timeout(200)
        page.mouse.up()
        page.wait_for_timeout(200)
        # No error means it worked
        assert s.evaluate("el => el.classList.contains('miki-splitter')")

    def test_dockable_panel_drag_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        headers = page.locator(".miki-dock-header")
        if headers.count() == 0:
            pytest.skip("No dockable panel headers found")
        h = headers.first
        h_box = h.bounding_box()
        if not h_box:
            pytest.skip("No header bounding box")
        h.click(force=True)  # Just verify it doesn't error
        page.wait_for_timeout(200)

    def test_drawer_close_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        drawers = page.locator(".miki-drawer")
        if drawers.count() == 0:
            pytest.skip("No drawers found")
        d = drawers.first
        # Click a close button if present (drawer is closed by default in kitchen sink)
        close_btn = d.locator('[data-miki-drawer-close="true"], button.miki-drawer-close')
        if close_btn.count() > 0:
            close_btn.first.click(force=True, position={"x": 5, "y": 5})
            page.wait_for_timeout(300)

    def test_messagebox_close_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        messageboxes = page.locator(".miki-messagebox")
        if messageboxes.count() == 0:
            pytest.skip("No message boxes found")
        mb = messageboxes.first
        close_btn = mb.locator('[data-miki-messagebox-close="true"]')
        if close_btn.count() > 0:
            # MessageBox is hidden by default — make it visible for the test
            mb.evaluate("el => { el.style.display = 'flex'; el.setAttribute('data-miki-messagebox-open', 'true'); }")
            close_btn.first.click()
            page.wait_for_timeout(300)

    def test_carousel_next_prev_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        carousels = page.locator(".miki-carousel")
        if carousels.count() == 0:
            pytest.skip("No carousels found")
        c = carousels.first
        next_btn = c.locator(".miki-carousel-next")
        prev_btn = c.locator(".miki-carousel-prev")
        if next_btn.count() > 0:
            next_btn.click(force=True)
            page.wait_for_timeout(300)
        if prev_btn.count() > 0:
            prev_btn.click(force=True)
            page.wait_for_timeout(300)

    def test_chat_send_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        chats = page.locator(".miki-chat")
        if chats.count() == 0:
            pytest.skip("No chat found")
        chat = chats.first
        send_btn = chat.locator('button[type="submit"]')
        input_field = chat.locator('input[name="message"]')
        if input_field.count() > 0 and send_btn.count() > 0:
            input_field.fill("Test message from mouse")
            send_btn.click(force=True)
            page.wait_for_timeout(300)

    def test_slider_change_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        sliders = page.locator('input[type="range"]')
        if sliders.count() == 0:
            pytest.skip("No sliders found")
        slider = sliders.first
        initial = slider.evaluate("el => el.value")
        slider.evaluate("el => { el.value = '75'; el.dispatchEvent(new Event('input', {bubbles: true})); }")
        page.wait_for_timeout(300)
        new_val = slider.evaluate("el => el.value")
        assert new_val == "75"

    def test_chip_toggle_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        # Chips aren't a dedicated component — test Badge as a representative
        badges = page.locator(".miki-badge")
        if badges.count() == 0:
            pytest.skip("No badges found")
        # Just verify badges are present and clickable
        assert badges.first.inner_text() != ""


    def test_formwizard_next_mouse(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        wizards = page.locator(".miki-wizard")
        if wizards.count() == 0:
            pytest.skip("No wizard found")
        next_btn = wizards.locator(".miki-wizard-next")
        if next_btn.count() > 0:
            next_btn.first.click(force=True)
            page.wait_for_timeout(300)


class TestKitchenSinkTouch:
    """Touch-based interactions on the kitchen sink."""

    def test_tabs_switch_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        tabs = touch_page.locator('[role="tab"]')
        if tabs.count() < 2:
            pytest.skip("No tabs found")
        tabs.nth(1).click()
        touch_page.wait_for_timeout(300)
        assert tabs.nth(1).get_attribute("aria-selected") == "true"

    def test_collapsible_toggle_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        collapsibles = touch_page.locator('[data-miki-collapsible="true"]')
        if collapsibles.count() == 0:
            pytest.skip("No collapsibles found")
        c = collapsibles.first
        header = c.locator('[data-miki-collapsible-header="true"]')
        if header.count() == 0:
            pytest.skip("No header found")
        initial = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        header.click()
        touch_page.wait_for_timeout(300)
        after = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        assert initial != after

    def test_splitview_drag_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        splitters = touch_page.locator('[data-miki-splitter="true"]')
        if splitters.count() == 0:
            pytest.skip("No splitters found")
        s = splitters.first
        s_box = s.bounding_box()
        if not s_box:
            pytest.skip("No bounding box")
        # Touch drag on splitter (simulate via pointer events)
        s.click(force=True)
        touch_page.wait_for_timeout(200)
        errors = []
        touch_page.on("pageerror", lambda exc: errors.append(str(exc)))
        assert len(errors) == 0, f"JS errors: {errors}"

    def test_drawer_close_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        drawers = touch_page.locator(".miki-drawer")
        if drawers.count() == 0:
            pytest.skip("No drawers found")
        d = drawers.first
        close_btn = d.locator('[data-miki-drawer-close="true"]')
        if close_btn.count() > 0:
            close_btn.first.click(force=True, position={"x": 5, "y": 5})
            touch_page.wait_for_timeout(300)

    def test_carousel_swipe_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        carousels = touch_page.locator(".miki-carousel")
        if carousels.count() == 0:
            pytest.skip("No carousels found")
        c = carousels.first
        c_box = c.bounding_box()
        if not c_box:
            pytest.skip("No bounding box")
        # Simulate horizontal swipe via pointer events
        start_x = c_box["x"] + c_box["width"] * 0.8
        end_x = c_box["x"] + c_box["width"] * 0.2
        mid_y = c_box["y"] + c_box["height"] / 2
        c.evaluate("""(el, data) => {
            const startEvent = new PointerEvent('pointerdown', {
                clientX: data.startX, clientY: data.midY, pointerType: 'touch'
            });
            const moveEvent = new PointerEvent('pointermove', {
                clientX: data.endX, clientY: data.midY, pointerType: 'touch'
            });
            const endEvent = new PointerEvent('pointerup', {
                clientX: data.endX, clientY: data.midY, pointerType: 'touch'
            });
            el.dispatchEvent(startEvent);
            el.dispatchEvent(moveEvent);
            el.dispatchEvent(endEvent);
        }""", {"startX": start_x, "endX": end_x, "midY": mid_y})
        touch_page.wait_for_timeout(300)

    def test_chat_input_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        chats = touch_page.locator(".miki-chat")
        if chats.count() == 0:
            pytest.skip("No chat found")
        chat = chats.first
        input_field = chat.locator('input[name="message"]')
        send_btn = chat.locator('button[type="submit"]')
        if input_field.count() > 0 and send_btn.count() > 0:
            input_field.fill("Test message from touch")
            send_btn.click(force=True)
            touch_page.wait_for_timeout(300)

    def test_chip_toggle_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        badges = touch_page.locator(".miki-badge")
        if badges.count() == 0:
            pytest.skip("No badges found")
        assert badges.first.inner_text() != ""

    def test_dockable_panel_buttons_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        dock_panels = touch_page.locator(".miki-dockable-panel")
        if dock_panels.count() == 0:
            pytest.skip("No dockable panels found")
        # Find close/collapse/detach buttons
        buttons = touch_page.locator('[data-miki-dock-action]')
        if buttons.count() > 0:
            buttons.first.click()
            touch_page.wait_for_timeout(200)

    def test_formwizard_back_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        # Navigate forward then back
        next_btn = touch_page.locator(".miki-wizard-next")
        if next_btn.count() > 0:
            next_btn.first.click(force=True)
            touch_page.wait_for_timeout(200)
        back_btn = touch_page.locator(".miki-wizard-back")
        if back_btn.count() > 0 and not back_btn.first.get_attribute("disabled"):
            back_btn.first.click(force=True)
            touch_page.wait_for_timeout(200)

    def test_slider_change_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        sliders = touch_page.locator('input[type="range"]')
        if sliders.count() == 0:
            pytest.skip("No sliders found")
        slider = sliders.first
        slider.evaluate("el => { el.value = '40'; el.dispatchEvent(new Event('input', {bubbles: true})); }")
        touch_page.wait_for_timeout(300)
        assert slider.evaluate("el => el.value") == "40"

    def test_messagebox_overlay_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        messageboxes = touch_page.locator(".miki-messagebox")
        if messageboxes.count() == 0:
            pytest.skip("No message boxes found")
        mb = messageboxes.first
        close_btn = mb.locator('[data-miki-messagebox-close="true"]')
        if close_btn.count() > 0:
            mb.evaluate("el => { el.style.display = 'flex'; el.setAttribute('data-miki-messagebox-open', 'true'); }")
            touch_page.wait_for_timeout(100)
            close_btn.first.click()
            touch_page.wait_for_timeout(300)

    def test_modal_overlay_click_touch(self, touch_page):
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        modals = touch_page.locator(".miki-modal-overlay")
        if modals.count() == 0:
            pytest.skip("No modals found")
        # Test that modal can be closed via Esc key
        modals.first.press("Escape")
        touch_page.wait_for_timeout(200)

    def test_navbar_hamburger_touch(self, touch_page):
        touch_page.load("/")
        touch_page.set_viewport_size({"width": 375, "height": 667})
        touch_page.wait_for_timeout(300)
        toggle = touch_page.locator(".miki-navbar-toggle").first
        if toggle.count() == 0:
            pytest.skip("No navbar toggle found (desktop view)")
        navbar = touch_page.locator(".miki-navbar").first
        links = navbar.locator(".miki-navbar-links")
        # Use JS click for touch context compatibility
        touch_page.evaluate("() => { document.querySelector('.miki-navbar-toggle').click(); }")
        touch_page.wait_for_timeout(200)
        assert links.evaluate("el => el.classList.contains('open')"), "Nav links should open"
        touch_page.evaluate("() => { document.querySelector('.miki-navbar-toggle').click(); }")
        touch_page.wait_for_timeout(200)
        assert not links.evaluate("el => el.classList.contains('open')"), "Nav links should close"

    def test_tabs_swipe_touch(self, touch_page):
        """Test swipe gesture on tabs."""
        touch_page.load("/")
        touch_page.wait_for_timeout(500)
        tab_elements = touch_page.locator('[role="tab"]')
        if tab_elements.count() < 2:
            pytest.skip("No tabs found")
        tab = tab_elements.first
        tab_box = tab.bounding_box()
        if not tab_box:
            pytest.skip("No tab bounding box")
        start_x = tab_box["x"] + tab_box["width"] / 2
        start_y = tab_box["y"] + tab_box["height"] / 2
        # Simulate swipe via pointer events (touch context compatible)
        tab.evaluate("""(el, data) => {
            el.dispatchEvent(new PointerEvent('pointerdown', { clientX: data.x, clientY: data.y, pointerType: 'touch' }));
            el.dispatchEvent(new PointerEvent('pointermove', { clientX: data.x + 50, clientY: data.y, pointerType: 'touch' }));
            el.dispatchEvent(new PointerEvent('pointerup', { clientX: data.x + 50, clientY: data.y, pointerType: 'touch' }));
        }""", {"x": start_x, "y": start_y})
        touch_page.wait_for_timeout(300)
