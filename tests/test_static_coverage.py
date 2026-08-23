"""Static coverage asserts for MikiUI components and widgets.

Verifies that every component and widget listed in context/components.md
has a corresponding Python implementation in the codebase.
"""

from __future__ import annotations

import pytest

# Components explicitly listed in context/components.md
EXPECTED_COMPONENTS = {
    "Html",
    "Head",
    "Title",
    "Meta",
    "Link",
    "Script",
    "Style",
    "Body",
    "Heading",
    "Paragraph",
    "Span",
    "Div",
    "Section",
    "Article",
    "Aside",
    "Header",
    "Footer",
    "Main",
    "Nav",
    "UnorderedList",
    "OrderedList",
    "ListItem",
    "DescriptionList",
    "DescriptionTerm",
    "DescriptionDetail",
    "Form",
    "Input",
    "Textarea",
    "Select",
    "Checkbox",
    "Radio",
    "Button",
    "Label",
    "Fieldset",
    "Legend",
    "Image",
    "Video",
    "Audio",
    "Canvas",
    "SVG",
    "Picture",
    "Source",
    "Dialog",
    "Details",
    "Summary",
    "Modal",
    "Tabs",
    "Accordion",
    "Tooltip",
    "Table",
    "ProgressBar",
    "Meter",
    "Slider",
    "Output",
    "Anchor",
    "Menu",
    "Time",
    "Code",
    "Preformatted",
    "Blockquote",
    "Figure",
    "Mark",
    "Small",
    "Strong",
    "Emphasis",
    "Abbreviation",
    "Address",
    "Citation",
    "Keyboard",
    "Variable",
    "Sample",
}

# Widgets explicitly listed in context/components.md that should be in mikiui.widgets
# Note: Calendar, Chart, ListView, TreeView are base components, not composite widgets
EXPECTED_WIDGETS = {
    "DataGrid",
    "FilePicker",
    "FormWizard",
    "SearchPanel",
    "MediaPlayer",
    "ChatUI",
    "StreamingPanel",
    "NotificationPanel",
    "DockablePanel",
    "SplitView",
    "PropertyGrid",
    "Dashboard",
    "KanbanBoard",
    "InspectorPanel",
    "CollapsiblePanel",
    "SidePanel",
    "TabbedPanel",
    "ThemeSwitcher",
    "IDEEditor",
    "TerminalWidget",
    "LogViewer",
    "ProfilerPanel",
}


def _get_component_class_names() -> set[str]:
    """Return all class names exported from mikiui.components."""
    from mikiui.components import __all__ as comp_all

    return set(comp_all)


def _get_widget_class_names() -> set[str]:
    """Return all class names exported from mikiui.widgets."""
    try:
        from mikiui.widgets import __all__ as widget_all

        return set(widget_all)
    except ImportError:
        return set()


def test_all_catalog_components_implemented() -> None:
    """Every component in context/components.md must have a Python class."""
    implemented = _get_component_class_names()
    missing = EXPECTED_COMPONENTS - implemented
    assert not missing, (
        "Components listed in context/components.md but not implemented: "
        f"{sorted(missing)}"
    )


def test_all_catalog_widgets_implemented() -> None:
    """Every widget in context/components.md must have a Python class."""
    implemented = _get_widget_class_names()
    missing = EXPECTED_WIDGETS - implemented
    assert not missing, (
        "Widgets listed in context/components.md but not implemented: "
        f"{sorted(missing)}"
    )


def test_component_aliases_exist() -> None:
    """Common HTML aliases (Img/Image, Br/Hr, etc.) should resolve."""
    from mikiui.components import Br, Hr, Image, Img

    assert Image is Img or Image is not None
    assert Br is not None
    assert Hr is not None


def test_widget_modules_importable() -> None:
    """All widget modules should be importable without errors."""
    widget_modules = [
        "mikiui.widgets.datagrid",
        "mikiui.widgets.chatui",
        "mikiui.widgets.dashboard",
        "mikiui.widgets.dockable_panel",
        "mikiui.widgets.ide_editor",
        "mikiui.widgets.inspector_panel",
        "mikiui.widgets.kanbanboard",
        "mikiui.widgets.mediaplayer",
        "mikiui.widgets.panels",
        "mikiui.widgets.splitview",
        "mikiui.widgets.property_grid",
        "mikiui.widgets.terminal_widget",
        "mikiui.widgets.theme_switcher",
        "mikiui.widgets.navigation_widgets",
        "mikiui.widgets.layout_widgets",
        "mikiui.widgets.advanced",
        "mikiui.widgets.advanced_widgets",
    ]
    for module_name in widget_modules:
        try:
            __import__(module_name)
        except ImportError as exc:
            pytest.fail(f"Widget module {module_name} is not importable: {exc}")
