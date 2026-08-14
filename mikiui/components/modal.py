"""Modal component (custom overlay built from a ``<div>``)."""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import Div


class Modal(Component):
    """A modal dialog: an overlay ``<div>`` containing a content panel.

    Use ``open`` to control visibility (toggled client-side via Alpine/HTMX).
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        open: bool = False,
        title: str | None = None,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("role", "dialog")
        attrs.setdefault("aria-modal", "true")
        if title:
            attrs.setdefault("aria-label", title)
        panel = Div(*children, class_="miki-modal-panel")
        overlay = Div(panel, class_="miki-modal-overlay")
        super().__init__(overlay, **attrs)
        self._open = open

    @property
    def open(self) -> bool:
        return self._open
