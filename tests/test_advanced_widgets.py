"""Tests for the new advanced, auth, and Qt-style widgets."""

from __future__ import annotations

import pytest

from mikiui.widgets import (
    ColorPicker,
    CollapsiblePanel,
    DatePicker,
    Dial,
    FormWizard,
    GroupBox,
    LCDNumber,
    LoginForm,
    LogViewer,
    MdiArea,
    MdiSubWindow,
    MenuBar,
    MessageBox,
    NotificationPanel,
    ProgressDialog,
    ScrollPanel,
    SearchPanel,
    SidePanel,
    SignupForm,
    SplashScreen,
    StackedPanel,
    StatusBar,
    StreamingPanel,
    TabbedPanel,
    Toolbar,
    ToolboxPanel,
)


def test_form_wizard_contains_steps_and_nav():
    w = FormWizard([("Step 1", "first"), ("Step 2", "second")], current=0)
    html = w.to_html()
    assert "Step 1" in html and "Step 2" in html
    assert "<ol" in html
    assert "miki-wizard" in html


def test_search_panel_has_query_input_and_results():
    html = SearchPanel().to_html()
    assert 'name="q"' in html
    assert 'id="search-results"' in html
    assert "Search" in html


def test_streaming_panel_has_log_and_status():
    html = StreamingPanel("Live").to_html()
    assert 'id="streaming-log"' in html
    assert 'role="log"' in html
    assert 'role="status"' in html
    assert "Live" in html


def test_notification_panel_toast():
    p = NotificationPanel()
    html = p.to_html()
    assert 'role="log"' in html
    toast = p.toast("Hello").to_html()
    assert "miki-toast" in toast
    assert "Hello" in toast


def test_login_form_fields():
    html = LoginForm().to_html()
    assert 'type="password"' in html
    assert 'name="username"' in html
    assert 'name="password"' in html
    assert "Log in" in html


def test_signup_form_fields():
    html = SignupForm().to_html()
    assert 'name="name"' in html
    assert 'name="email"' in html
    assert 'type="password"' in html
    assert 'name="password"' in html
    assert 'name="password_confirm"' in html
    assert "Sign up" in html


def test_groupbox_fieldset_and_legend():
    html = GroupBox("Settings", "body").to_html()
    assert "<fieldset" in html
    assert "<legend" in html
    assert "Settings" in html


def test_scroll_panel_overflow():
    html = ScrollPanel("x").to_html()
    assert "overflow" in html
    assert "auto" in html


def test_stacked_panel_pages():
    html = StackedPanel([("A", "page a"), ("B", "page b")]).to_html()
    assert "page a" in html and "page b" in html
    assert "A" in html and "B" in html


def test_toolbox_panel_collapsible():
    html = ToolboxPanel({"Tools": ["hammer", "wrench"]}).to_html()
    assert "<details" in html
    assert "<summary" in html
    assert "Tools" in html
    assert "hammer" in html


def test_toolbar_role():
    html = Toolbar("a", "b").to_html()
    assert 'role="toolbar"' in html


def test_statusbar_role():
    html = StatusBar("ready").to_html()
    assert 'role="status"' in html
    assert "ready" in html


def test_menubar_items():
    html = MenuBar([("File", [("Open", "/open"), ("Save", "/save")])]).to_html()
    assert "<nav" in html
    assert "File" in html
    assert 'href="/open"' in html


def test_splash_screen():
    html = SplashScreen("Loading", "please wait").to_html()
    assert "miki-splash" in html
    assert "Loading" in html
    assert "please wait" in html


def test_messagebox_alertdialog():
    html = MessageBox("Oops", "bad", kind="error").to_html()
    assert 'role="alertdialog"' in html
    assert "Oops" in html
    assert "bad" in html


def test_colorpicker():
    html = ColorPicker().to_html()
    assert 'type="color"' in html
    assert 'name="color"' in html


def test_datepicker():
    html = DatePicker(value="2026-01-02").to_html()
    assert 'type="date"' in html
    assert 'value="2026-01-02"' in html


def test_progress_dialog():
    html = ProgressDialog("Wait", "working", value=40).to_html()
    assert "<dialog" in html
    assert "<progress" in html


def test_lcd_number_value():
    html = LCDNumber(42, digits=6).to_html()
    assert "miki-lcd" in html
    assert "000042" in html


def test_dial():
    html = Dial(value=30).to_html()
    assert 'type="range"' in html
    assert 'value="30"' in html
    assert "miki-dial" in html


def test_mdi_area_and_subwindow():
    sub = MdiSubWindow("Win1", "content")
    html = MdiArea(sub).to_html()
    assert "miki-mdiarea" in html
    assert "Win1" in html
    assert "content" in html


def test_collapsible_panel():
    html = CollapsiblePanel("More", "detail", open=True).to_html()
    assert "<details" in html
    assert "<summary" in html
    assert "More" in html
    assert "open" in html


def test_side_panel():
    html = SidePanel("right", "x").to_html()
    assert "miki-sidepanel" in html
    assert "miki-side-right" in html


def test_tabbed_panel():
    html = TabbedPanel([("T1", "c1"), ("T2", "c2")]).to_html()
    assert "miki-tabbedpanel" in html
    assert "T1" in html and "T2" in html


def test_log_viewer_severity():
    html = LogViewer([("error", "boom"), "plain"]).to_html()
    assert "miki-log-error" in html
    assert "boom" in html
    assert "miki-log-info" in html
    assert "plain" in html
