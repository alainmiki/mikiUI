"""VS Code-like SplitView editor area component.

A recursive grid-based editor area with multiple resizable groups, each
containing a tab bar and content panels. Supports drag-and-drop between
groups, splitters, and keyboard navigation.

Features (matching VS Code):
- Multiple editor groups in a grid layout
- Tab bars with close buttons
- Draggable splitters between groups
- Drag tabs between groups
- Double-click splitter to maximize/restore
- Arrow keys for fine adjustment
- ARIA-compliant roles and properties
- i18n hooks
- Self-contained CSS and JS assets served from ``static/``

Static assets
-------------
CSS and JS are loaded from the component's ``static/`` directory via the
MikiUI static asset registry.  When the server is running, assets are served
at:

* ``/_miki/components/splitview/static/splitview.css``
* ``/_miki/components/splitview/static/splitview.js``

For offline/testing scenarios where static files are unavailable, the
component falls back to inline embedding automatically.

Example
-------
>>> from mikiui.components import SplitView, EditorGroup, EditorTab
>>>
>>> SplitView(
...     EditorGroup(
...         [EditorTab("main.py", "print('hello')"), EditorTab("readme.md", "# README")],
...         active=0,
...     ),
...     EditorGroup(
...         [EditorTab("utils.py", "def helper(): pass")],
...     ),
...     orientation="horizontal",
... )
"""

from __future__ import annotations

import os
import uuid
from typing import Any

from ..base import Component
from ..button import Button
from ..html import Div, Section, Span


_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.join(_THIS_DIR, "static")
_CSS_PATH = os.path.join(_STATIC_DIR, "splitview.css")
_JS_PATH = os.path.join(_STATIC_DIR, "splitview.js")

_CSS_URL = "/_miki/components/splitview/static/splitview.css"
_JS_URL = "/_miki/components/splitview/static/splitview.js"


def _read_asset(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


class EditorTab:
    """Represents a single tab in an editor group.

    Parameters
    ----------
    label : str
        Tab label (e.g. filename).
    content : Any
        Tab content.
    closable : bool
        Whether the tab shows a close button.
    icon : str | None
        Optional icon name.
    """

    __slots__ = ("label", "content", "closable", "icon")

    def __init__(
        self,
        label: str,
        content: Any,
        closable: bool = True,
        icon: str | None = None,
    ) -> None:
        self.label = label
        self.content = content
        self.closable = closable
        self.icon = icon


class EditorGroup(Component):
    """A single editor group with a tab bar and content panels.

    Parameters
    ----------
    tabs : list[EditorTab | tuple]
        List of tabs in this group. Each tab can be an ``EditorTab`` instance
        or a ``(label, content)`` tuple (or ``(label, content, icon)``).
    active : int
        Index of the initially active tab (default 0).
    group_id : str | None
        Unique group ID. Auto-generated if not provided.
    **attrs : Additional HTML attributes.
    """

    tag = "div"

    def __init__(
        self,
        tabs: list[EditorTab | tuple],
        active: int = 0,
        group_id: str | None = None,
        **attrs: Any,
    ) -> None:
        if not tabs:
            raise ValueError("EditorGroup requires at least one tab")

        normalized_tabs: list[EditorTab] = []
        for tab in tabs:
            if isinstance(tab, EditorTab):
                normalized_tabs.append(tab)
            elif isinstance(tab, (tuple, list)):
                if len(tab) == 2:
                    normalized_tabs.append(EditorTab(tab[0], tab[1]))
                elif len(tab) == 3:
                    normalized_tabs.append(EditorTab(tab[0], tab[1], icon=tab[2]))
                else:
                    raise ValueError(
                        "Tab tuple must be (label, content) or (label, content, icon)"
                    )
            else:
                raise ValueError(
                    "Tabs must be EditorTab instances or (label, content) tuples"
                )

        tabs = normalized_tabs
        active = max(0, min(active, len(tabs) - 1))
        group_id = group_id or f"eg-{uuid.uuid4().hex[:8]}"

        user_class = attrs.pop("class_", "")
        attrs["class_"] = f"miki-editor-group {user_class}".strip()
        attrs.setdefault("role", "region")
        attrs.setdefault("aria-label", "Editor group")
        attrs.setdefault("data-miki-editor-group", "true")
        attrs.setdefault("data-group-id", group_id)

        tabbar_children: list[Any] = []
        for i, tab in enumerate(tabs):
            is_active = i == active
            tab_class = "miki-editor-tab" + (" miki-editor-tab-active" if is_active else "")

            tab_content_parts: list[Any] = []
            if tab.icon:
                tab_content_parts.append(Span(tab.icon, class_="miki-editor-tab-icon"))
            tab_content_parts.append(tab.label)

            if tab.closable:
                close_btn = Button(
                    "×",
                    type="button",
                    class_="miki-editor-tab-close",
                    role="button",
                    aria_label="Close tab",
                    **{
                        "data-miki-tab-close": "true",
                        "data-miki-tab-group": group_id,
                        "data-miki-tab-index": str(i),
                        "onclick": (
                            f"mikiEditorArea.closeTab('{group_id}', {i});"
                        ),
                    },
                )
                tab_content_parts.append(close_btn)

            tab_btn_attrs: dict[str, Any] = {
                "type": "button",
                "role": "tab",
                "id": f"{group_id}-tab-{i}",
                "aria_selected": str(is_active).lower(),
                "aria_controls": f"{group_id}-panel-{i}",
                "tabindex": "0" if is_active else "-1",
                "class_": tab_class,
                "data_miki_tab": "true",
                "data_miki_tab_group": group_id,
                "data_miki_tab_index": str(i),
                "draggable": "true",
                "onclick": f"mikiEditorArea.showTab('{group_id}', {i});",
            }
            tabbar_children.append(Div(*tab_content_parts, **tab_btn_attrs))

        tabbar = Div(
            *tabbar_children,
            class_="miki-editor-tabbar",
            role="tablist",
            aria_label="Editor tabs",
            **{"data-miki-tab-group": group_id},
        )

        content_panels: list[Any] = []
        for i, tab in enumerate(tabs):
            is_active = i == active
            panel_attrs: dict[str, Any] = {
                "role": "tabpanel",
                "id": f"{group_id}-panel-{i}",
                "aria_labeledby": f"{group_id}-tab-{i}",
                "class_": "miki-editor-content"
                + (" miki-editor-content-active" if is_active else ""),
            }
            if not is_active:
                panel_attrs["hidden"] = True

            content_panels.append(Section(tab.content, **panel_attrs))

        content_container = Div(
            *content_panels, class_="miki-editor-content-container"
        )

        super().__init__(tabbar, content_container, **attrs)


class SplitView(Component):
    """VS Code-like editor area with multiple resizable groups.

    Arranges editor groups in a recursive grid layout. Each group has its own
    tab bar and content panels. Groups are separated by draggable splitters.

    Layout is defined by the number of children:

    * 1 child — single editor group.
    * 2 children — split horizontally or vertically.
    * 4 children — 2×2 grid (auto-arranged).

    Parameters
    ----------
    *groups : EditorGroup | SplitView
        Editor groups or nested split views.
    orientation : str
        ``"horizontal"`` (side-by-side) or ``"vertical"`` (stacked).
    min_size : int
        Minimum pixel size for each pane.
    separator_width : int
        Width/height of the splitter handle.
    **attrs : Additional HTML attributes.

    Example
    -------
    >>> SplitView(
    ...     EditorGroup([EditorTab("main.py", "code")]),
    ...     EditorGroup([EditorTab("utils.py", "code")]),
    ...     orientation="horizontal",
    ... )
    """

    tag = "div"

    def __init__(
        self,
        *groups: Any,
        orientation: str = "horizontal",
        min_size: int = 150,
        separator_width: int = 4,
        **attrs: Any,
    ) -> None:
        if orientation not in ("horizontal", "vertical"):
            raise ValueError("orientation must be 'horizontal' or 'vertical'")

        if len(groups) not in (1, 2, 4):
            raise ValueError("SplitView requires 1, 2, or 4 children")

        if len(groups) == 4:
            top_row = SplitView(
                groups[0],
                groups[1],
                orientation="horizontal",
                min_size=min_size,
                separator_width=separator_width,
            )
            bottom_row = SplitView(
                groups[2],
                groups[3],
                orientation="horizontal",
                min_size=min_size,
                separator_width=separator_width,
            )
            groups = (top_row, bottom_row)
            orientation = "vertical"

        user_class = attrs.pop("class_", "")
        base_class = "miki-splitview miki-editor-area"
        attrs["class_"] = f"{base_class} {user_class}".strip()
        attrs.setdefault("role", "group")
        attrs.setdefault("aria-label", "Editor area")
        attrs.setdefault("data-miki-splitview", "true")
        attrs.setdefault("data-miki-editor-area", "true")
        attrs.setdefault("data-orientation", orientation)
        attrs.setdefault("data-min-size", str(min_size))

        is_horizontal = orientation == "horizontal"

        container_class = "miki-splitview-container"
        if is_horizontal:
            container_class += " miki-split-h"
        else:
            container_class += " miki-split-v"

        attrs["class_"] = attrs["class_"] + " " + container_class

        # Try to load static assets; fall back to inline embedding when the
        # static file server is not available (offline/testing).
        css_content = _read_asset(_CSS_PATH)
        js_content = _read_asset(_JS_PATH)

        use_static = bool(css_content and js_content)

        asset_children: list[Any] = []
        if use_static:
            from ..html import Link, Script

            asset_children.append(
                Link(
                    rel="stylesheet",
                    href=_CSS_URL,
                    id="miki-splitview-css",
                )
            )
            asset_children.append(
                Script(
                    src=_JS_URL,
                    id="miki-splitview-js",
                    type="text/javascript",
                )
            )
        else:
            from ..html import Style, Script

            if css_content:
                asset_children.append(Style(css_content, id="miki-splitview-css"))
            if js_content:
                asset_children.append(
                    Script(js_content, id="miki-splitview-js", type="text/javascript")
                )

        children_list: list[Any] = []
        for i, group in enumerate(groups):
            if i > 0:
                splitter = Div(
                    "",
                    class_="miki-splitter miki-splitter-editor",
                    role="separator",
                    aria_orientation="horizontal" if is_horizontal else "vertical",
                    tabindex="0",
                    **{
                        "data-miki-splitter": "true",
                        "data-miki-splitter-index": str(i - 1),
                        "data-miki-editor-splitter": "true",
                    },
                )
                children_list.append(splitter)
            children_list.append(group)

        super().__init__(*asset_children, *children_list, **attrs)
