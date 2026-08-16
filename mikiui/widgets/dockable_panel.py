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

from ..components import Button, Div, Span
from ..components.base import Component


class DockablePanel(Component):
    """A dockable panel with collapse, close, and detach controls.

    Uses ``data-miki-*`` attributes for client-side state management via
    ``miki_ui.js``.  All actions (toggle, close, detach) work without
    Alpine.js.

    The header contains clearly-labeled action buttons with ``aria-label``
    and ``title`` attributes so users always know what each button does.

    Parameters
    ----------
    title : str
        Panel title shown in header.
    *content : Any
        Panel body content.
    dock : str
        Default dock position: 'top', 'left', 'right', 'bottom', 'floating'.
    collapsible : bool
        Show collapse/expand toggle button.
    closeable : bool
        Show close button.
    minimal : bool
        Show only the title bar (minimal height).
    resizable : bool
        Allow resize by dragging edges.
    detachable : bool
        Allow detaching as floating panel.
    open : bool
        Initial expanded state.
    close_on_escape : bool
        Close floating panel with ESC key (default: True).
    snap_threshold : int
        Pixel threshold for snap-to-edge during drag (default: 100).
    dock_width : str
        CSS width when docked to left/right (default: '300px').
    dock_height : str
        CSS height when docked to top/bottom (default: '300px').
    float_width : str
        CSS width when floating (default: '40vw').
    float_height : str
        CSS height when floating (default: '50vh').
    **attrs : Additional HTML attributes.
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
        close_on_escape: bool = True,
        snap_threshold: int = 100,
        dock_width: str = "300px",
        dock_height: str = "300px",
        float_width: str = "40vw",
        float_height: str = "50vh",
        **attrs: Any,
    ) -> None:
        dock_positions = ("top", "left", "right", "bottom", "floating")
        if dock not in dock_positions:
            raise ValueError(f"dock must be one of {dock_positions}, got {dock!r}")

        attrs.setdefault("class_", "miki-dockable-panel")
        attrs.setdefault("role", "region")
        attrs.setdefault("aria_labelledby", f"{title}-dock-title")
        attrs.setdefault("tabindex", "0")
        attrs.setdefault("data-miki-dockable", "true")
        attrs.setdefault("data-miki-dock-position", dock)

        if dock == "floating":
            dock_state = "floating"
            attrs.setdefault("data-miki-close-on-escape", "true" if close_on_escape else "false")
        elif not open:
            dock_state = "collapsed"
        else:
            dock_state = "docked"
        attrs.setdefault("data-miki-dock-state", dock_state)

        # Customization attributes for JS
        attrs.setdefault("data-snap-threshold", str(snap_threshold))
        attrs.setdefault("data-dock-width", dock_width)
        attrs.setdefault("data-dock-height", dock_height)
        attrs.setdefault("data-float-width", float_width)
        attrs.setdefault("data-float-height", float_height)

        # CSS custom properties for initial rendering (JS reads data-* attrs, CSS reads vars)
        attrs.setdefault("style", "")
        style_parts = [p.strip() for p in attrs["style"].split(";") if p.strip()]
        style_parts.append(f"--miki-dock-width:{dock_width}")
        style_parts.append(f"--miki-dock-height:{dock_height}")
        style_parts.append(f"--miki-float-width:{float_width}")
        style_parts.append(f"--miki-float-height:{float_height}")
        attrs["style"] = ";".join(style_parts)

        # Add dock position CSS class for initial rendering
        attrs["class_"] = attrs.get("class_", "miki-dockable-panel") + f" miki-dock-{dock}"

        if not open:
            attrs["class_"] += " miki-dock-collapsed"

        header_children: list[Any] = []

        dock_indicator = self._make_dock_indicator(dock)
        header_children.append(dock_indicator)

        title_span = Span(
            title,
            class_="miki-dock-title",
            id=f"{title}-dock-title",
            title=f"Dock position: {dock}",
        )
        header_children.append(title_span)

        # Spacer to push buttons to the right
        header_children.append(Span(class_="miki-dock-spacer", style="flex-grow: 1;"))

        if collapsible:
            toggle_icon = Span("▼", class_="miki-dock-toggle-icon")
            header_children.append(
                Button(
                    toggle_icon,
                    type="button",
                    class_="miki-dock-toggle",
                    role="button",
                    aria_label="Collapse panel" if open else "Expand panel",
                    title="Collapse / Expand panel",
                    **{"data-miki-dock-action": "toggle"},
                )
            )

        if closeable:
            header_children.append(
                Button(
                    "×",
                    type="button",
                    class_="miki-dock-close",
                    role="button",
                    aria_label="Close panel",
                    title="Close panel",
                    **{"data-miki-dock-action": "close"},
                )
            )

        if detachable:
            header_children.append(
                Button(
                    "⇋",
                    type="button",
                    class_="miki-dock-detach",
                    role="button",
                    aria_label="Detach panel (float)",
                    title="Detach panel (float) / Dock panel",
                    **{"data-miki-dock-action": "detach"},
                )
            )

        header = Div(
            *header_children,
            class_="miki-dock-header",
            draggable="true",
            **{"data-miki-dock-header": "true"},
        )

        body = Div(
            *content,
            class_="miki-dock-body",
            style="height: auto;",
        )

        if resizable:
            resize_child = Span(
                "",
                class_="miki-dock-resizable-handle",
                role="separator",
                aria_orientation="horizontal",
            )
            header = Div(
                *header_children,
                resize_child,
                class_="miki-dock-header miki-dock-resizable",
                draggable="true",
            )

        super().__init__(header, body, **attrs)

    def _make_dock_indicator(self, dock: str) -> Any:
        """Create a visual indicator showing the dock position.

        The indicator is a colored strip on the left edge of the header
        with a directional arrow icon, making the dock position obvious.
        """
        indicators = {
            "top": ("▲", "miki-dock-indicator miki-dock-top", "Docked to top edge"),
            "left": ("◀", "miki-dock-indicator miki-dock-left", "Docked to left edge"),
            "right": ("▶", "miki-dock-indicator miki-dock-right", "Docked to right edge"),
            "bottom": ("▼", "miki-dock-indicator miki-dock-bottom", "Docked to bottom edge"),
            "floating": ("◎", "miki-dock-indicator miki-dock-floating", "Floating (detached)"),
        }
        icon, cls, tooltip = indicators.get(dock, indicators["right"])
        return Span(icon, class_=cls, title=tooltip, role="img", aria_label=tooltip)
