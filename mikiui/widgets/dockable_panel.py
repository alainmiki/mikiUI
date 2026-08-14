"""DockablePanel widget: a titled panel with a mock drag handle."""

from __future__ import annotations

from typing import Any

from ..components import Div, H3, Section, Span
from ..components.base import Component


class DockablePanel(Component):
    """Render a dockable panel with a header (title + drag handle) and body.

    :param title: panel title shown in the header.
    :param content: arbitrary child content placed in the panel body.
    """

    tag = "section"

    def __init__(self, title: str, *content: Any, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-dockable")
        header = Div(
            H3(title),
            Span("⠿", class_="miki-dock-handle", aria_label="Drag handle"),
            class_="miki-dock-header",
        )
        body = Div(*content, class_="miki-dock-body")
        super().__init__(header, body, **attrs)
