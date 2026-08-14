"""Tests for the mikiui.widgets package."""

from __future__ import annotations

import pytest

from mikiui.engine import render
from mikiui.widgets import (
    ChatUI,
    Dashboard,
    DataGrid,
    DockablePanel,
    IDEEditor,
    InspectorPanel,
    KanbanBoard,
    MediaPlayer,
    PropertyGrid,
    SplitView,
    TerminalWidget,
)


def test_datagrid_contains_table_and_columns():
    grid = DataGrid(["Name", "Age"], [["Alice", 30], ["Bob", 25]])
    html = render(grid)
    assert "<table" in html
    assert "Name" in html
    assert "Alice" in html


def test_datagrid_pagination_slices_rows():
    rows = [[f"r{i}"] for i in range(25)]
    grid = DataGrid(["C"], rows, pagination=True, page=0, page_size=10)
    html = render(grid)
    assert html.count("<tr") > 1  # header + 10 rows
    assert "r0" in html and "r10" not in html


def test_mediaplayer_video_has_source():
    player = MediaPlayer("movie.mp4", kind="video", eq="Bass")
    html = render(player)
    assert "<video" in html
    assert 'src="movie.mp4"' in html
    assert "controls" in html
    assert "Bass" in html


def test_mediaplayer_audio():
    player = MediaPlayer("song.mp3", kind="audio")
    html = render(player)
    assert "<audio" in html
    assert 'src="song.mp3"' in html


def test_dashboard_grid():
    dash = Dashboard("a", "b", "c", columns=3)
    html = render(dash)
    assert "miki-dashboard" in html
    assert html.count("miki-dashboard-card") == 3


def test_kanbanboard_contains_column():
    board = KanbanBoard({"Todo": ["x"], "Done": ["y"]})
    html = render(board)
    assert "Todo" in html
    assert "Done" in html


def test_chatui_contains_input_and_messages():
    chat = ChatUI([{"role": "user", "text": "hi"}, {"role": "bot", "text": "hello"}])
    html = render(chat)
    assert "<input" in html
    assert "hi" in html
    assert "miki-chat-bot" in html


def test_ideeditor_contains_content():
    editor = IDEEditor("print(1)", language="python")
    html = render(editor)
    assert "miki-ide" in html
    assert "print(1)" in html


def test_dockable_panel_title():
    panel = DockablePanel("My Panel", "body")
    html = render(panel)
    assert "My Panel" in html
    assert "<section" in html


def test_splitview():
    sv = SplitView("left", "right", orientation="horizontal")
    html = render(sv)
    assert "miki-splitview" in html
    assert "left" in html
    assert "right" in html


def test_property_grid_inputs():
    grid = PropertyGrid({"name": "Miki", "age": 3})
    html = render(grid)
    assert "<table" in html
    assert 'name="name"' in html
    assert 'value="Miki"' in html


def test_inspector_panel_from_object():
    class Thing:
        def __init__(self):
            self.a = 1
            self.b = "two"

    panel = InspectorPanel(Thing())
    html = render(panel)
    assert 'name="a"' in html
    assert 'name="b"' in html


def test_inspector_panel_fallback():
    panel = InspectorPanel(42)
    html = render(panel)
    assert "42" in html


def test_terminal_widget_lines():
    term = TerminalWidget(["line1", "line2"])
    html = render(term)
    assert "miki-terminal" in html
    assert "line1" in html
    assert "line2" in html
