"""DockablePanel widget: a titled panel with collapsible content."""

from __future__ import annotations

from typing import Any

from ..components import Div, H3, Section, Span
from ..components.base import Component


class DockablePanel(Component):
    """A dockable panel with header, drag handle, and collapsible body.

    The panel can be collapsed/expanded via the toggle button. For floating
    or drag-to-dock behavior, integrate with Alpine.js in a parent container.

    :param title: panel title shown in the header.
    :param content: arbitrary child content placed in the panel body.
    :param collapsible: If ``True`` (default), show expand/collapse toggle.
    :param open: If ``True`` (default), panel starts expanded.
    :param attrs: Extra HTML attributes.

    Example::

        DockablePanel("Properties", PropertyGrid(), collapsible=True)
        DockablePanel("Output", LogViewer(...), open=False)
    """

    tag = "section"

    def __init__(
        self,
        title: str,
        *content: Any,
        collapsible: bool = True,
        open: bool = True,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class", "miki-dockable")
        attrs.setdefault("role", "region")
        attrs.setdefault("aria_labelledby", f"{title}-dock-title")

        icon = "▼" if open else "►"
        header_children = [
            Span(title, class_="miki-dock-title", id=f"{title}-dock-title"),
            Span(icon, class_="miki-dock-toggle", role="button", aria_label="Toggle panel"),
            Span("⠿", class_="miki-dock-handle", aria_label="Drag handle"),
        ]

        header = Div(*header_children, class_="miki-dock-header")

        body = Div(*content, class_="miki-dock-body")
        if not open:
            body = Div(*content, class_="miki-dock-body", style="display:none")

        super().__init__(header, body, **attrs)
