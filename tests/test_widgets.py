"""Tests for the mikiui.widgets package."""

from __future__ import annotations

from mikiui.engine import render
from mikiui.widgets import (
    Carousel,
    ChatUI,
    Dashboard,
    DataGrid,
    DockablePanel,
    Drawer,
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


def test_datagrid_search_fields():
    grid = DataGrid(["Name", "Email"], [["Alice", "a@b.c"]], search_fields=["Name", "Email"])
    html = render(grid)
    assert "<select" in html
    assert "search_field" in html
    assert "Name" in html and "Email" in html


def test_datagrid_htmx_attrs():
    grid = DataGrid(["A"], [["x"]], htmx_get="/api/data", htmx_target="#grid")
    html = render(grid)
    assert "data-miki-htmx-get" in html
    assert "data-miki-htmx-target" in html


def test_datagrid_search_input_has_data_attr():
    grid = DataGrid(["A"], [["x"]], search=True)
    html = render(grid)
    assert 'data-miki-search="true"' in html


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


def test_datagrid_has_search_box():
    grid = DataGrid(["Name", "Age"], [["Alice", 30], ["Bob", 25]], search=True)
    html = render(grid)
    assert "data-miki-search" in html


def test_datagrid_has_sort_indicators():
    grid = DataGrid(["Name", "Age"], [["Alice", 30], ["Bob", 25]], sortable=True)
    html = render(grid)
    assert "miki-sort-indicator" in html


def test_datagrid_has_filter_inputs():
    grid = DataGrid(["Name", "Age"], [["Alice", 30], ["Bob", 25]], filterable=True)
    html = render(grid)
    assert "data-miki-filter" in html


def test_datagrid_has_pagination_controls():
    grid = DataGrid(["Name"], [["a"], ["b"], ["c"]], pagination=True, page_size=2)
    html = render(grid)
    assert "data-miki-pagination" in html


def test_kanbanboard_has_drag_drop():
    board = KanbanBoard({"Todo": ["x"], "Done": ["y"]})
    html = render(board)
    assert "data-sort-item" in html
    assert 'draggable="true"' in html


def test_chatui_has_data_attributes():
    chat = ChatUI([{"role": "user", "text": "hi"}])
    html = render(chat)
    assert "data-miki-chat" in html


def test_dockable_panel_has_data_actions():
    panel = DockablePanel("My Panel", "body", closeable=True, detachable=True)
    html = render(panel)
    assert "data-miki-dockable" in html
    assert "data-miki-dock-action" in html


def test_splitview_has_data_attributes():
    sv = SplitView("left", "right", orientation="horizontal")
    html = render(sv)
    assert "data-miki-splitview" in html
    assert 'data-orientation="horizontal"' in html


def test_datagrid_sortable_headers_have_data_field():
    grid = DataGrid(["Name", "Age"], [["Alice", 30], ["Bob", 25]], sortable=True)
    html = render(grid)
    assert "data-miki-sort-field" in html


def test_datagrid_sort_indicator_has_data_attr():
    grid = DataGrid(["Name", "Age"], [["Alice", 30], ["Bob", 25]], sortable=True)
    html = render(grid)
    assert 'data-miki-sort-indicator="true"' in html


def test_splitview_splitter_has_data_attr():
    sv = SplitView("left", "right", orientation="horizontal")
    html = render(sv)
    assert 'data-miki-splitter="true"' in html


def test_splitview_has_min_size():
    sv = SplitView("left", "right", orientation="horizontal", min_size=150)
    html = render(sv)
    assert 'data-min-size="150"' in html


def test_dockable_panel_toggle_action():
    panel = DockablePanel("My Panel", "body", collapsible=True)
    html = render(panel)
    assert 'data-miki-dock-action="toggle"' in html


def test_kanbanboard_has_data_attr():
    board = KanbanBoard({"Todo": ["x"], "Done": ["y"]})
    html = render(board)
    assert 'data-miki-kanban="true"' in html


def test_kanbanboard_columns_have_data_attr():
    board = KanbanBoard({"Todo": ["x"], "Done": ["y"]})
    html = render(board)
    assert "data-miki-kanban-column" in html


def test_kanbanboard_items_have_data_attr():
    board = KanbanBoard({"Todo": ["x"], "Done": ["y"]})
    html = render(board)
    assert 'data-miki-kanban-item="true"' in html


def test_chatui_has_chat_form_attr():
    chat = ChatUI([{"role": "user", "text": "hi"}])
    html = render(chat)
    assert 'data-miki-chat-form="true"' in html


def test_chatui_has_typing_indicator():
    chat = ChatUI([{"role": "user", "text": "hi"}])
    html = render(chat)
    assert "miki-chat-typing" in html


def test_collapsible_panel_has_state_attr():
    from mikiui.widgets import CollapsiblePanel

    panel = CollapsiblePanel("More", "detail", open=True)
    html = render(panel)
    assert 'data-miki-state="open"' in html


def test_filepicker_input_has_data_attr():
    from mikiui.widgets import FilePicker

    picker = FilePicker(name="file", label="Drop files")
    html = render(picker)
    assert 'data-miki-file-input="true"' in html


def test_dockable_panel_no_alpine_xdata():
    panel = DockablePanel("My Panel", "body")
    html = render(panel)
    assert "x_data" not in html


def test_splitview_no_alpine_xdata():
    sv = SplitView("left", "right", orientation="horizontal")
    html = render(sv)
    assert "x_data" not in html


def test_datagrid_no_alpine_xdata():
    grid = DataGrid(["Name", "Age"], [["Alice", 30], ["Bob", 25]])
    html = render(grid)
    assert "x_data" not in html


def test_drawer_close_has_data_attr():
    drawer = Drawer("content", title="Drawer", side="left")
    html = render(drawer)
    assert 'data-miki-drawer-close="true"' in html


def test_carousel_nav_has_data_attrs():
    carousel = Carousel("img1.jpg", "img2.jpg")
    html = render(carousel)
    assert 'data-miki-carousel-prev="true"' in html
    assert 'data-miki-carousel-next="true"' in html


def test_chatui_has_data_attrs():
    chat = ChatUI([{"role": "user", "text": "hi"}])
    html = render(chat)
    assert "data-miki-chat-form" in html


def test_drawer_toggle_component():
    from mikiui.widgets import DrawerToggle

    html = render(DrawerToggle("Open", target="#my-drawer"))
    assert "data-miki-drawer-toggle" in html
    assert "data-miki-drawer-target" in html


def test_dockable_panel_draggable_header():
    panel = DockablePanel("P", "body")
    html = render(panel)
    assert 'data-miki-dock-header="true"' in html


def test_splitview_resize_mode_horizontal():
    sv = SplitView("left", "right", orientation="horizontal", resize_mode="horizontal")
    html = render(sv)
    assert 'data-resize-mode="horizontal"' in html


def test_splitview_resize_mode_vertical():
    sv = SplitView("top", "bottom", orientation="vertical", resize_mode="vertical")
    html = render(sv)
    assert 'data-resize-mode="vertical"' in html


def test_splitview_resize_mode_both():
    sv = SplitView("a", "b", orientation="horizontal", resize_mode="both")
    html = render(sv)
    assert 'data-resize-mode="both"' in html


def test_splitview_invalid_resize_mode():
    import pytest
    with pytest.raises(ValueError, match="resize_mode"):
        SplitView("left", "right", resize_mode="diagonal")


def test_splitview_has_data_split_pane():
    sv = SplitView("left", "right")
    html = render(sv)
    assert 'data-miki-split-pane="first"' in html
    assert 'data-miki-split-pane="second"' in html


def test_dockable_panel_custom_dock():
    panel = DockablePanel("Title", "body", dock="top")
    html = render(panel)
    assert "miki-dock-top" in html
    assert 'data-miki-dock-position="top"' in html


def test_dockable_panel_invalid_dock():
    import pytest
    with pytest.raises(ValueError, match="dock"):
        DockablePanel("Title", "body", dock="center")


def test_dockable_panel_custom_dimensions():
    panel = DockablePanel("Title", "body", dock="left", dock_width="400px", dock_height="200px",
                          float_width="60vw", float_height="70vh")
    html = render(panel)
    assert "data-dock-width" in html
    assert "data-dock-height" in html
    assert "data-float-width" in html
    assert "data-float-height" in html


def test_dockable_panel_snap_threshold():
    panel = DockablePanel("Title", "body", snap_threshold=50)
    html = render(panel)
    assert 'data-snap-threshold="50"' in html


def test_dockable_panel_toggle_icon():
    panel = DockablePanel("Title", "body", collapsible=True)
    html = render(panel)
    assert "miki-dock-toggle-icon" in html


def test_dockable_panel_close_on_escape():
    panel = DockablePanel("Title", "body", dock="floating", close_on_escape=False)
    html = render(panel)
    assert 'data-miki-close-on-escape="false"' in html


def test_dockable_panel_has_css_custom_props():
    panel = DockablePanel("Title", "body", dock_width="350px", float_height="60vh")
    html = render(panel)
    assert "--miki-dock-width:350px" in html
    assert "--miki-float-height:60vh" in html


def test_dockable_panel_has_dock_indicator():
    panel = DockablePanel("Title", "body", dock="right")
    html = render(panel)
    assert "miki-dock-indicator" in html
    assert "▶" in html
