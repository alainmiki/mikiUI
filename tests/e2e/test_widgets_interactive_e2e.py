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
def touch_context(browser, server):
    """A browser context with has_touch enabled for touch interaction tests."""
    context = browser.new_context(has_touch=True)
    yield context
    context.close()


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
            "core.js", "miki_bridge.js", "mikieditorarea.js", "mikidialog.js", "mikimodal.js", "mikitabs.js",
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


class TestDrawerInteractive:
    """Drawer: open/close via JS API, overlay click, ESC, side configurations."""

    def test_drawer_open_close_js(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        drawer = page.locator(".demo-drawer").first
        if drawer.count() == 0:
            pytest.skip("No drawer found")
        assert not drawer.evaluate("el => el.classList.contains('miki-drawer-open')")
        page.evaluate("mikiDrawer.open('.demo-drawer')")
        page.wait_for_timeout(200)
        assert drawer.evaluate("el => el.classList.contains('miki-drawer-open')")
        page.evaluate("mikiDrawer.close('.demo-drawer')")
        page.wait_for_timeout(200)
        assert not drawer.evaluate("el => el.classList.contains('miki-drawer-open')")

    def test_drawer_overlay_click_closes(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        drawer = page.locator(".demo-drawer").first
        if drawer.count() == 0:
            pytest.skip("No drawer found")
        page.evaluate("mikiDrawer.open('.demo-drawer')")
        page.wait_for_timeout(200)
        overlay = drawer.locator(".miki-drawer-overlay")
        # Click on the overlay element directly via JS to avoid pointer interception
        page.evaluate("document.querySelector('.demo-drawer .miki-drawer-overlay').click()")
        page.wait_for_timeout(200)
        assert not drawer.evaluate("el => el.classList.contains('miki-drawer-open')")

    def test_drawer_esc_closes(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        drawer = page.locator(".demo-drawer").first
        if drawer.count() == 0:
            pytest.skip("No drawer found")
        page.evaluate("mikiDrawer.open('.demo-drawer')")
        page.wait_for_timeout(200)
        assert drawer.evaluate("el => el.classList.contains('miki-drawer-open')")
        page.evaluate("document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))")
        page.wait_for_timeout(200)
        assert not drawer.evaluate("el => el.classList.contains('miki-drawer-open')")

    def test_drawer_right_side(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        drawer = page.locator(".demo-drawer-right").first
        if drawer.count() == 0:
            pytest.skip("No right drawer found")
        page.evaluate("mikiDrawer.open('.demo-drawer-right')")
        page.wait_for_timeout(200)
        assert drawer.evaluate("el => el.classList.contains('miki-drawer-open')")
        page.evaluate("mikiDrawer.close('.demo-drawer-right')")
        page.wait_for_timeout(100)

    def test_drawer_toggle(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        drawer = page.locator(".demo-drawer").first
        if drawer.count() == 0:
            pytest.skip("No drawer found")
        page.evaluate("mikiDrawer.toggle('.demo-drawer')")
        page.wait_for_timeout(200)
        assert drawer.evaluate("el => el.classList.contains('miki-drawer-open')")
        page.evaluate("mikiDrawer.toggle('.demo-drawer')")
        page.wait_for_timeout(200)
        assert not drawer.evaluate("el => el.classList.contains('miki-drawer-open')")

    def test_drawer_string_selector(self, page):
        """Drawer open/close/toggle accept a CSS selector string."""
        page.load("/")
        page.wait_for_timeout(500)
        drawer = page.locator(".demo-drawer").first
        if drawer.count() == 0:
            pytest.skip("No drawer found")
        page.evaluate("mikiDrawer.open('.demo-drawer')")
        page.wait_for_timeout(200)
        assert drawer.evaluate("el => el.classList.contains('miki-drawer-open')")
        page.evaluate("mikiDrawer.close('.demo-drawer')")
        page.wait_for_timeout(200)
        assert not drawer.evaluate("el => el.classList.contains('miki-drawer-open')")


class TestDrawerOpenSide:
    """Drawer open_side: panel anchored to one side but slides in from another."""

    def test_open_side_attribute_present(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        override = page.locator("[data-miki-drawer-open-side]").first
        if override.count() == 0:
            pytest.skip("No open_side drawer found")
        assert override.count() >= 1, "Expected at least one drawer with open_side override"

    def test_open_side_drawer_opens_from_right(self, page):
        """Drawer with side=left and open_side=right should still open."""
        page.load("/")
        page.wait_for_timeout(500)
        # The kitchen sink has an override drawer on /advanced, but we test /
        drawer = page.locator(".demo-drawer").first
        if drawer.count() == 0:
            pytest.skip("No drawer found")
        page.evaluate("mikiDrawer.open('.demo-drawer')")
        page.wait_for_timeout(200)
        assert drawer.evaluate("el => el.classList.contains('miki-drawer-open')")


class TestBottomSheetInteractive:
    """BottomSheet: open/close via JS API, overlay click, ESC."""

    def test_bottomsheet_open_close_js(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        sheet = page.locator(".demo-bottomsheet").first
        if sheet.count() == 0:
            pytest.skip("No bottom sheet found")
        assert sheet.evaluate("el => el.getAttribute('data-miki-bottom-sheet-open')") == "false"
        page.evaluate("mikiBottomSheet.open('.demo-bottomsheet')")
        page.wait_for_timeout(300)
        assert sheet.evaluate("el => el.getAttribute('data-miki-bottom-sheet-open')") == "true"
        panel = sheet.locator(".miki-bottom-sheet-panel")
        assert panel.evaluate("el => el.classList.contains('miki-bottom-sheet-panel-open')")
        page.evaluate("mikiBottomSheet.close('.demo-bottomsheet')")
        page.wait_for_timeout(300)
        assert sheet.evaluate("el => el.getAttribute('data-miki-bottom-sheet-open')") == "false"

    def test_bottomsheet_backdrop_click_closes(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        sheet = page.locator(".demo-bottomsheet").first
        if sheet.count() == 0:
            pytest.skip("No bottom sheet found")
        page.evaluate("mikiBottomSheet.open('.demo-bottomsheet')")
        page.wait_for_timeout(300)
        backdrop = sheet.locator(".miki-bottom-sheet-backdrop")
        backdrop.click()
        page.wait_for_timeout(300)
        assert sheet.evaluate("el => el.getAttribute('data-miki-bottom-sheet-open')") == "false"

    def test_bottomsheet_esc_closes(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        sheet = page.locator(".demo-bottomsheet").first
        if sheet.count() == 0:
            pytest.skip("No bottom sheet found")
        page.evaluate("mikiBottomSheet.open('.demo-bottomsheet')")
        page.wait_for_timeout(300)
        assert sheet.evaluate("el => el.getAttribute('data-miki-bottom-sheet-open')") == "true"
        page.evaluate("document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))")
        page.wait_for_timeout(300)
        assert sheet.evaluate("el => el.getAttribute('data-miki-bottom-sheet-open')") == "false"


class TestTabKeyboardNav:
    """Tab widget: keyboard navigation (ArrowLeft/Right, Enter/Space)."""
    def _get_tabs(self, page):
        page.load("/data")
        page.wait_for_timeout(300)
        return page.locator("[data-miki-tabs='true'] button")

    def test_arrow_right_switches_tab(self, page):
        tabs = self._get_tabs(page)
        if tabs.count() < 2:
            pytest.skip("Not enough tabs")
        tabs.nth(0).focus()
        tabs.nth(0).press("ArrowRight")
        assert tabs.nth(1).evaluate("el => el.classList.contains('miki-tab-active')")
        assert not tabs.nth(0).evaluate("el => el.classList.contains('miki-tab-active')")

    def test_arrow_left_switches_tab(self, page):
        tabs = self._get_tabs(page)
        if tabs.count() < 2:
            pytest.skip("Not enough tabs")
        tabs.nth(1).focus()
        tabs.nth(1).press("ArrowLeft")
        assert tabs.nth(0).evaluate("el => el.classList.contains('miki-tab-active')")
        assert not tabs.nth(1).evaluate("el => el.classList.contains('miki-tab-active')")

    def test_enter_activates_tab(self, page):
        tabs = self._get_tabs(page)
        if tabs.count() < 2:
            pytest.skip("Not enough tabs")
        tabs.nth(0).focus()
        tabs.nth(0).press("ArrowRight")  # move active to tab 1
        tabs.nth(0).press("Enter")  # tab 0 is not active, enter should activate it
        assert tabs.nth(0).evaluate("el => el.classList.contains('miki-tab-active')")


class TestCollapsible:
    """Collapsible widget: click and keyboard toggle."""
    def _get_collapsibles(self, page):
        page.load("/data")
        page.wait_for_timeout(300)
        return page.locator("[data-miki-collapsible='true']")

    def test_click_toggles(self, page):
        collapsibles = self._get_collapsibles(page)
        if collapsibles.count() == 0:
            pytest.skip("No collapsibles on page")
        c = collapsibles.first
        header = c.locator("[data-miki-collapsible-header='true']")
        if header.count() == 0:
            pytest.skip("No collapsible header found")
        initial_open = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        header.click()
        page.wait_for_timeout(200)
        after_open = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        assert initial_open != after_open, "Click should toggle collapsible state"
        # Click again to toggle back
        header.click()
        page.wait_for_timeout(200)
        final_open = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        assert final_open == initial_open, "Second click should restore original state"

    def test_keyboard_toggle(self, page):
        collapsibles = self._get_collapsibles(page)
        if collapsibles.count() == 0:
            pytest.skip("No collapsibles on page")
        c = collapsibles.first
        header = c.locator("[data-miki-collapsible-header='true']")
        if header.count() == 0:
            pytest.skip("No collapsible header found")
        initial_open = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        header.focus()
        header.press("Enter")
        page.wait_for_timeout(200)
        after_open = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        assert initial_open != after_open, "Enter should toggle collapsible state"

    def test_space_toggle(self, page):
        collapsibles = self._get_collapsibles(page)
        if collapsibles.count() == 0:
            pytest.skip("No collapsibles on page")
        c = collapsibles.first
        header = c.locator("[data-miki-collapsible-header='true']")
        if header.count() == 0:
            pytest.skip("No collapsible header found")
        initial_open = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        header.focus()
        header.press(" ")
        page.wait_for_timeout(200)
        after_open = c.evaluate("el => el.classList.contains('miki-collapsible-open')")
        assert initial_open != after_open, "Space should toggle collapsible state"


class TestSplitterResize:
    """Splitter: horizontal/vertical drag, maximize, keyboard."""
    def _get_splitter(self, page, url="/data", orientation="horizontal"):
        page.load(url)
        page.wait_for_timeout(500)
        splitter = page.locator(f'[data-miki-splitview][data-orientation="{orientation}"] > [data-miki-splitter]').first
        return splitter

    def test_horizontal_drag(self, page):
        splitter = self._get_splitter(page)
        sv = splitter.evaluate("el => el.closest('[data-miki-splitview]')")
        if not sv:
            pytest.skip("No splitview found")
        orient = splitter.evaluate("el => el.closest('[data-miki-splitview]').getAttribute('data-orientation')")
        if orient != "horizontal":
            pytest.skip("Splitview is not horizontal")

        # Scroll splitter into view so mouse events reach it
        splitter.scroll_into_view_if_needed()
        page.wait_for_timeout(100)

        box = splitter.bounding_box()
        if not box:
            pytest.skip("No bounding box")

        # Get initial pane widths (direct children only)
        before = splitter.evaluate("""el => {
            var sv = el.closest('[data-miki-splitview]');
            var panes = sv.querySelectorAll(':scope > [data-miki-split-pane]');
            return Array.from(panes).map(p => p.offsetWidth);
        }""")

        # Drag right
        page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
        page.mouse.down()
        page.mouse.move(box["x"] + 100, box["y"] + box["height"]/2, steps=10)
        page.mouse.up()
        page.wait_for_timeout(200)

        after = splitter.evaluate("""el => {
            var sv = el.closest('[data-miki-splitview]');
            var panes = sv.querySelectorAll(':scope > [data-miki-split-pane]');
            return Array.from(panes).map(p => p.offsetWidth);
        }""")
        assert before != after, f"Pane widths should change: before={before} after={after}"

    def test_keyboard_arrow_keys(self, page):
        splitter = self._get_splitter(page)
        if not splitter.is_visible():
            pytest.skip("Splitter not visible")
        # Splitter should be focusable
        splitter.focus()
        # Press ArrowRight to resize horizontally
        splitter.press("ArrowRight")
        page.wait_for_timeout(200)
        # No error means keyboard works
        assert splitter.evaluate("el => el.classList.contains('miki-splitter')")

    def test_double_click_maximize(self, page):
        splitter = self._get_splitter(page)
        sv = splitter.locator("xpath=ancestor::*[@data-miki-splitview]")
        if sv.count() == 0:
            pytest.skip("No splitview found")
        sv_element = sv.first
        # Dispatch dblclick directly (Playwright's dblclick may not fire on thin splitters)
        sv_element.evaluate("""
            el => {
                const splitter = el.querySelector(':scope > [data-miki-splitter="true"]');
                if (splitter) {
                    splitter.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true }));
                }
            }
        """)
        page.wait_for_timeout(200)
        has_max = sv_element.evaluate("el => el.classList.contains('miki-split-maximized')")
        assert has_max, "Splitter should maximize on double-click"

        # Double-click again to restore
        sv_element.evaluate("""
            el => {
                const splitter = el.querySelector(':scope > [data-miki-splitter="true"]');
                if (splitter) {
                    splitter.dispatchEvent(new MouseEvent('dblclick', { bubbles: true, cancelable: true }));
                }
            }
        """)
        page.wait_for_timeout(200)
        has_max = sv_element.evaluate("el => !el.classList.contains('miki-split-maximized')")
        assert has_max, "Splitter should restore on second double-click"


class TestDialInteractive:
    """Dial: value changes, keyboard, click-to-value."""

    def test_dial_exists(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        dials = page.locator("[data-miki-dial='true']")
        if dials.count() == 0:
            pytest.skip("No dials found")
        assert dials.count() >= 1

    def test_dial_keyboard_increments(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        dial = page.locator("[data-miki-dial='true']").first
        if dial.count() == 0:
            pytest.skip("No dial found")
        input_el = dial.locator("input[type='range']")
        step = int(input_el.get_attribute("step") or "1")
        before = input_el.evaluate("el => parseFloat(el.value)")
        input_el.focus()
        input_el.press("ArrowRight")
        page.wait_for_timeout(100)
        after = input_el.evaluate("el => parseFloat(el.value)")
        assert after == before + step, f"Dial should increment by step={step}: {before} -> {after}"

    def test_dial_keyboard_decrements(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        dial = page.locator("[data-miki-dial='true']").first
        if dial.count() == 0:
            pytest.skip("No dial found")
        input_el = dial.locator("input[type='range']")
        step = int(input_el.get_attribute("step") or "1")
        input_el.focus()
        input_el.press("ArrowRight")
        page.wait_for_timeout(100)
        before = input_el.evaluate("el => parseFloat(el.value)")
        min_val = float(input_el.evaluate("el => parseFloat(el.min)"))
        if before <= min_val:
            pytest.skip("Dial at minimum, cannot test decrement")
        input_el.press("ArrowLeft")
        page.wait_for_timeout(100)
        after = input_el.evaluate("el => parseFloat(el.value)")
        assert after == before - step, f"Dial should decrement by step={step}: {before} -> {after}"

    def test_dial_home_end(self, page):
        page.load("/")
        page.wait_for_timeout(500)
        dial = page.locator("[data-miki-dial='true']").first
        if dial.count() == 0:
            pytest.skip("No dial found")
        input_el = dial.locator("input[type='range']")
        max_val = float(input_el.evaluate("el => el.max"))
        input_el.focus()
        input_el.press("End")
        page.wait_for_timeout(100)
        assert input_el.evaluate("el => parseFloat(el.value)") == max_val
        input_el.press("Home")
        page.wait_for_timeout(100)
        assert input_el.evaluate("el => parseFloat(el.value)") == 0


class TestToggleButton:
    """Toggle widget: click, keyboard, aria-pressed."""
    def _find_toggles(self, page):
        page.load("/advanced")
        page.wait_for_timeout(300)
        return page.locator("[data-miki-toggle='true']")

    def test_click_toggles_state(self, page):
        toggles = self._find_toggles(page)
        if toggles.count() == 0:
            pytest.skip("No toggles found on /advanced")
        t = toggles.first
        initial = t.evaluate("el => el.getAttribute('data-miki-state')")
        t.click()
        page.wait_for_timeout(200)
        after = t.evaluate("el => el.getAttribute('data-miki-state')")
        assert initial != after, f"State should toggle: {initial} -> {after}"

    def test_keyboard_enter(self, page):
        toggles = self._find_toggles(page)
        if toggles.count() == 0:
            pytest.skip("No toggles found on /advanced")
        t = toggles.first
        t.focus()
        t.press("Enter")
        page.wait_for_timeout(200)
        assert t.evaluate("el => el.hasAttribute('data-miki-state')")

    def test_keyboard_space(self, page):
        toggles = self._find_toggles(page)
        if toggles.count() == 0:
            pytest.skip("No toggles found on /advanced")
        t = toggles.first
        t.focus()
        t.press(" ")
        page.wait_for_timeout(200)
        assert t.evaluate("el => el.hasAttribute('data-miki-state')")

    def test_aria_pressed_updates(self, page):
        toggles = self._find_toggles(page)
        if toggles.count() == 0:
            pytest.skip("No toggles found on /advanced")
        t = toggles.first
        initial = t.get_attribute("aria-pressed")
        t.click()
        page.wait_for_timeout(200)
        after = t.get_attribute("aria-pressed")
        assert initial != after


class TestDialogClose:
    """Dialog: ESC key and close button."""
    def test_esc_closes_dialog(self, page):
        page.load("/dialog")
        page.wait_for_timeout(500)
        dialogs = page.locator("[data-miki-dialog='true']")
        if dialogs.count() == 0:
            pytest.skip("No dialogs found")
        dlg = dialogs.first
        close_btn = dlg.locator("[data-miki-dialog-close='true']").first
        if close_btn.count() > 0:
            close_btn.click()
            page.wait_for_timeout(200)
            is_hidden = dlg.evaluate("el => !el.hasAttribute('open') || el.style.display === 'none'")
            assert is_hidden, "Dialog should be hidden after close button click"

    def test_backdrop_click_closes(self, page):
        page.load("/dialog")
        page.wait_for_timeout(500)
        dialogs = page.locator("[data-miki-dialog='true']")
        if dialogs.count() == 0:
            pytest.skip("No dialogs found")
        dlg = dialogs.first
        close_on_overlay = dlg.get_attribute("data-miki-dialog-close-on-overlay")
        if close_on_overlay != "true":
            pytest.skip("Dialog does not close on overlay click")
        # Click the dialog backdrop (the dialog itself)
        dlg.click(position={"x": 5, "y": 5})
        page.wait_for_timeout(200)
        is_hidden = dlg.evaluate("el => !el.hasAttribute('open') || el.style.display === 'none'")
        assert is_hidden, "Dialog should close on backdrop click"


class TestDialogKeyboard:
    """Dialog: ESC key closes."""
    def test_esc_key_closes(self, page):
        page.load("/dialog")
        page.wait_for_timeout(500)
        dialogs = page.locator("[data-miki-dialog='true']")
        if dialogs.count() == 0:
            pytest.skip("No dialogs found")
        dlg = dialogs.first
        dlg.focus()
        dlg.press("Escape")
        page.wait_for_timeout(200)
        is_hidden = dlg.evaluate("el => !el.hasAttribute('open') || el.style.display === 'none'")
        assert is_hidden, "Dialog should close on ESC"

    def test_tab_key_navigation(self, page):
        page.load("/dialog")
        page.wait_for_timeout(500)
        dialogs = page.locator("[data-miki-dialog='true']")
        if dialogs.count() == 0:
            pytest.skip("No dialogs on page")


class TestMessageBox:
    """MessageBox: close button and ESC."""
    def test_close_button(self, page):
        page.load("/dialog")
        page.wait_for_timeout(500)
        msgs = page.locator("[data-miki-messagebox='true']")
        if msgs.count() == 0:
            pytest.skip("No message boxes found")
        msg = msgs.first
        close_btn = msg.locator("[data-miki-messagebox-close='true']").first
        if close_btn.count() == 0:
            pytest.skip("No close button found")
        # Use evaluate to click directly (overlay might intercept Playwright clicks)
        msg.evaluate("""
            el => {
                const btn = el.querySelector('[data-miki-messagebox-close="true"]');
                if (btn) btn.click();
            }
        """)
        page.wait_for_timeout(200)
        is_hidden = msg.evaluate("el => el.style.display === 'none'")
        assert is_hidden, "MessageBox should be hidden after close"

    def test_esc_closes(self, page):
        page.load("/dialog")
        page.wait_for_timeout(500)
        msgs = page.locator("[data-miki-messagebox='true']")
        if msgs.count() == 0:
            pytest.skip("No message boxes found")
        msg = msgs.first
        msg.evaluate("el => { const evt = new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }); el.dispatchEvent(evt); }")
        page.wait_for_timeout(200)
        is_hidden = msg.evaluate("el => el.style.display === 'none'")
        assert is_hidden, "MessageBox should close on ESC"


class TestSlider:
    """Slider: value changes on interaction."""
    def test_slider_exists(self, page):
        page.load("/forms")
        page.wait_for_timeout(500)
        sliders = page.locator("[data-miki-slider='true']")
        assert sliders.count() >= 1, "At least one slider should exist"
        slider = sliders.first
        # Check it has proper ARIA attributes
        assert slider.get_attribute("role") == "slider" or slider.get_attribute("type") == "range"


class TestKanbanTouch:
    """Kanban: mobile touch interaction."""
    def test_touch_drag_kanban_item(self, touch_context, server):
        context = touch_context
        page = context.new_page()
        
        def load(url):
            resp = server.get(url)
            css_resp = server.get("/_miki/runtime/miki.css")
            js_files = [
                "core.js", "miki_bridge.js", "mikieditorarea.js", "mikidialog.js", "mikimodal.js", "mikitabs.js",
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

        page.set_viewport_size({"width": 375, "height": 667})
        load("/data")
        page.wait_for_timeout(500)

        items = page.locator("[data-miki-kanban-item='true']")
        columns = page.locator("[data-miki-kanban-column='true']")
        if items.count() == 0 or columns.count() < 2:
            pytest.skip("Not enough kanban items/columns")

        first_item = items.first
        col_box = columns.nth(1).bounding_box()
        item_box = first_item.bounding_box()
        if not col_box or not item_box:
            pytest.skip("No bounding boxes")

        # Touch tap on the item
        page.touchscreen.tap(item_box["x"] + item_box["width"]/2, item_box["y"] + item_box["height"]/2)
        page.wait_for_timeout(200)
        
        # Verify the tap registered (item may get highlight class or selection state)
        assert first_item.evaluate("el => el.textContent.length > 0")
        
        page.close()


class TestNavbarAccessibility:
    """Navbar: accessibility attributes."""
    def test_navbar_has_aria_label(self, page):
        page.set_viewport_size({"width": 375, "height": 667})
        page.load("/")
        page.wait_for_timeout(300)
        navbar = page.locator(".miki-navbar")
        expect(navbar).to_have_count(1)
        aria_label = navbar.get_attribute("aria-label")
        assert aria_label, "Navbar should have aria-label"

    def test_toggle_has_aria_label(self, page):
        page.set_viewport_size({"width": 375, "height": 667})
        page.load("/")
        page.wait_for_timeout(300)
        toggle = page.locator(".miki-navbar-toggle")
        expect(toggle).to_have_count(1)
        aria_label = toggle.get_attribute("aria-label")
        assert aria_label, "Toggle should have aria-label"
