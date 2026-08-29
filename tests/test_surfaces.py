"""Tests for surface components."""

from __future__ import annotations

from mikiui.components.surfaces import (
    BottomNavigation,
    BottomSheet,
    FloatingActionButton,
    SafeAreaView,
)


def test_safe_area_view_defaults():
    v = SafeAreaView("hello")
    assert v.tag == "div"
    assert "miki-safe-area" in v.to_html()
    assert "padding-top: env(safe-area-inset-top, 0px)" in v.to_html()


def test_safe_area_view_specific_edges():
    v = SafeAreaView("hello", edges="top,bottom")
    html = v.to_html()
    assert "padding-top: env(safe-area-inset-top, 0px)" in html
    assert "padding-bottom: env(safe-area-inset-bottom, 0px)" in html
    assert "padding-left" not in html


def test_bottom_sheet_defaults():
    sheet = BottomSheet("content")
    assert sheet.tag == "div"
    assert 'role="dialog"' in sheet.to_html()
    assert 'aria-modal="true"' in sheet.to_html()
    assert 'aria-hidden="true"' in sheet.to_html()
    assert "miki-bottom-sheet-md" in sheet.to_html()


def test_bottom_sheet_with_title_and_closable():
    sheet = BottomSheet("content", title="Title", closable=True)
    html = sheet.to_html()
    assert 'aria-label="Title"' in html
    assert "miki-bottom-sheet-close" in html


def test_bottom_sheet_callbacks():
    sheet = BottomSheet("content", on_open="onOpen", on_close="onClose")
    html = sheet.to_html()
    assert 'data-miki-bottom-sheet-on-open="onOpen"' in html
    assert 'data-miki-bottom-sheet-on-close="onClose"' in html


def test_bottom_navigation_defaults():
    nav = BottomNavigation()
    assert nav.tag == "nav"
    assert 'role="tablist"' in nav.to_html()
    assert "miki-bottom-nav" in nav.to_html()


def test_bottom_navigation_active_index():
    nav = BottomNavigation(active=2)
    assert 'data-miki-active-index="2"' in nav.to_html()


def test_floating_action_button_defaults():
    fab = FloatingActionButton("+")
    assert fab.tag == "button"
    assert "miki-fab" in fab.to_html()
    assert 'aria-label="Action"' in fab.to_html()
    assert 'type="button"' in fab.to_html()


def test_floating_action_button_position_and_extended():
    fab = FloatingActionButton("Add", position="bottom-left", extended=True, aria_label="Add item")
    html = fab.to_html()
    assert "miki-fab-bottom-left" in html
    assert "miki-fab-extended" in html
    assert 'aria-label="Add item"' in html
