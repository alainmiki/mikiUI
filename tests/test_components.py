"""Tests for the public MikiUI components."""

from __future__ import annotations

from mikiui import (
    H1,
    Button,
    Calendar,
    Chart,
    Dialog,
    Div,
    FilePicker,
    Form,
    Input,
    ListView,
    P,
    Table,
    Tabs,
    Td,
    Th,
    Tr,
    TreeView,
)


def test_basic_components():
    assert "<div>" in Div("x").to_html()
    assert "<p>" in P("x").to_html()
    assert "<h1>" in H1("x").to_html()


def test_button_default_type():
    html = Button("Go").to_html()
    assert "<button" in html
    assert 'type="button"' in html


def test_input_type():
    html = Input(type="text", name="q").to_html()
    assert "<input" in html
    assert 'type="text"' in html


def test_form_tag():
    assert "<form" in Form(action="/submit").to_html()


def test_dialog_open():
    html_open = Dialog("hi", open=True).to_html()
    assert "open" in html_open
    html_closed = Dialog("hi").to_html()
    assert 'data-open' not in html_closed or 'open=false' in html_closed


def test_table_structure():
    html = Table(Tr(Th("H"), Td("D"))).to_html()
    assert "<table" in html
    assert "<tr>" in html
    assert "<th" in html and ">H</th>" in html
    assert "<td" in html and ">D</td>" in html


def test_chart_kinds_render_svg():
    for kind in ("bar", "line", "pie"):
        html = Chart([1, 2, 3], kind=kind).to_html()
        assert "<svg" in html


def test_chart_empty():
    html = Chart([]).to_html()
    assert "(no data)" in html


def test_tabs_role_and_offline():
    html = Tabs([("A", "a"), ("B", "b")]).to_html()
    assert 'role="tablist"' in html
    assert "mikiTabs.show" in html
    assert 'role="tab"' in html
    assert 'role="tabpanel"' in html
    assert 'aria-selected' in html


def test_calendar_grid():
    html = Calendar(year=2024, month=1).to_html()
    assert 'role="grid"' in html
    assert "miki-calendar" in html


def test_filepicker():
    html = FilePicker(label="Pick", name="f").to_html()
    assert 'type="file"' in html
    assert "miki-filepicker" in html
    assert 'for="f"' in html


def test_treeview():
    html = TreeView([("root", [("leaf", None)]), ("other", None)]).to_html()
    assert 'role="tree"' in html
    assert "<details" in html
    assert "<details" in html
    assert "<summary" in html and ">root</summary>" in html


def test_listview():
    html = ListView(["a", "b"], selected=0).to_html()
    assert 'role="listbox"' in html
    assert "miki-listview" in html
    assert 'aria-selected="true"' in html
