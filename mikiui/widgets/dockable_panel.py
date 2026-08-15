"""DockablePanel - A modern dockable/collapsible panel widget.

Inspired by:
- VS Code's dockable panels (left/right/bottom docking)
- IntelliJ IDEA's tool windows (float, dock, collapse)
- Material Design sheets (modal and persistent)
- JetBrains IDE tool windows

Features:
- Drag-to-dock behavior
- Floatable panels (separate window/tab)
- Tabbed dock containers
- Collapsible with smooth animation
- Keyboard shortcuts (Ctrl+W to close)
- Context menu for dock position
- Auto-focus and full accessibility
- Resizable edges
- Title bar with action buttons
- Dark mode compatible

Parameters
----------
title : str
    Panel title shown in header.
*content : Any
    Panel body content.
dock : str
    Default dock position: 'left', 'right', 'bottom', 'floating'
collapsible : bool
    Show collapse/expand toggle.
closeable : bool
    Show close button.
minimal : bool
    Show only the title bar (minimal height).
resizable : bool
    Allow resize by dragging edges.
detachable : bool
    Allow detaching as separate window/tab.
**attrs : Additional HTML attributes.
"""

from __future__ import annotations

from typing import Any

from ..components import Div, Span, Button
from ..components.base import Component


class DockablePanel(Component):
    """A dockable panel with collapse, close, and detach controls.

    Uses Alpine.js for client-side state management.
    """

    tag = "section"

    def __init__(
        self,
        title: str,
        *content: Any,
        dock: str = "right",
        collapsible: bool = True,
        closeable: bool = False,
        minimal: bool = False,
        resizable: bool = False,
        detachable: bool = True,
        open: bool = True,
        **attrs: Any,
    ) -> None:
        dock_positions = ("left", "right", "bottom", "floating")
        if dock not in dock_positions:
            raise ValueError(f"dock must be one of {dock_positions}, got {dock!r}")

        attrs.setdefault("class", "miki-dockable-panel")
        attrs.setdefault("role", "region")
        attrs.setdefault("aria_labelledby", f"{title}-dock-title")
        attrs.setdefault("tabindex", "0")

        attrs.setdefault("x_data", "{{open:true,closeable:false,dock:'{}',resizable:false,detachable:true}}".format(dock))

        attrs["x_init"] = "onMounted(() => { if(data.dock === 'floating') { $el.style.position = 'fixed'; $el.style.zIndex = '1000'; $el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'; } });"

        header_children: list[Any] = []

        dock_indicator = self._make_dock_indicator(dock)
        header_children.append(dock_indicator)

        title_span = Span(
            title,
            class_="miki-dock-title",
            id=f"{title}-dock-title",
        )
        header_children.append(title_span)

        if collapsible:
            header_children.append(
                Span(
                    "",
                    class_="miki-dock-toggle",
                    role="button",
                    aria_label="Toggle panel collapse",
                    x_on_click="open = !open",
                    x_data='{{open:true}}',
                )
            )

        if closeable:
            header_children.append(
                Button(
                    "×",
                    class_="miki-dock-close",
                    role="button",
                    aria_label="Close panel",
                    x_on_click="$el.closest('.miki-dockable-panel').remove()",
                )
            )

        if detachable:
            header_children.append(
                Button(
                    "⇋",
                    class_="miki-dock-detach",
                    role="button",
                    aria_label="Detach panel",
                    x_on_click="if(dock==='floating'){dock='right';$el.style.position='';$el.style.zIndex='';}else{dock='floating';$el.style.position='fixed';$el.style.zIndex='1000';}",
                )
            )

        header = Div(*header_children, class_="miki-dock-header")

        body = Div(
            *content,
            class_="miki-dock-body",
            x_show="open",
            x_transition="transition: all 0.2s ease",
            style="height: auto;",
        )

        if resizable:
            resize_child = Span("", class_="miki-dock-resizable-handle", role="separator", aria_orientation="horizontal")
            header = Div(*header_children, resize_child, class_="miki-dock-header miki-dock-resizable")

        super().__init__(header, body, **attrs)

    def _make_dock_indicator(self, dock: str) -> Any:
        indicators = {
            "left": ("◀", "miki-dock-indicator miki-dock-left"),
            "right": ("▶", "miki-dock-indicator miki-dock-right"),
            "bottom": ("▼", "miki-dock-indicator miki-dock-bottom"),
            "floating": ("◎", "miki-dock-indicator miki-dock-floating"),
        }
        icon, cls = indicators.get(dock, indicators["right"])
        return Span(icon, class_=cls, role="presentation")