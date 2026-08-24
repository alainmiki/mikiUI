"""Tests for splitview component."""

from __future__ import annotations

import pytest

from mikiui.components.splitview.splitview import EditorArea, EditorGroup, EditorTab


def test_editor_tab_defaults():
    tab = EditorTab("main.py", "print('hello')")
    assert tab.label == "main.py"
    assert tab.content == "print('hello')"
    assert tab.closable is True
    assert tab.icon is None


def test_editor_tab_with_icon():
    tab = EditorTab("main.py", "code", icon="python")
    assert tab.icon == "python"


def test_editor_tab_not_closable():
    tab = EditorTab("main.py", "code", closable=False)
    assert tab.closable is False


def test_editor_group_requires_tabs():
    with pytest.raises(ValueError):
        EditorGroup([])


def test_editor_group_defaults():
    group = EditorGroup([EditorTab("a.py", "code")])
    assert group.tag == "div"
    html = group.to_html()
    assert "miki-editor-group" in html


def test_editor_group_active_index():
    group = EditorGroup([EditorTab("a.py", "code"), EditorTab("b.py", "code")], active=1)
    html = group.to_html()
    assert "miki-editor-tab-active" in html
    assert "b.py" in html


def test_editor_group_accepts_tuples():
    group = EditorGroup([("a.py", "code")])
    assert group.tag == "div"
    html = group.to_html()
    assert "a.py" in html


def test_editor_area_defaults():
    area = EditorArea(EditorGroup([EditorTab("a.py", "code")]))
    assert area.tag == "div"
    html = area.to_html()
    assert "miki-editor-area" in html


def test_editor_area_orientation():
    area = EditorArea(EditorGroup([EditorTab("a.py", "code")]), orientation="vertical")
    html = area.to_html()
    assert "miki-split-v" in html
