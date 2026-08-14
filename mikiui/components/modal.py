"""Modal component (custom overlay built from a ``<div>``)."""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import Div


class Modal(Component):
    """A modal dialog: a fixed overlay ``<div>`` containing a content panel.

    Use ``open`` to control visibility.  Visibility is toggled client-side via
    the ``miki:swapped`` event and Alpine, or manually via HTMX targets.

    ``title`` adds an accessible ``aria-label`` and an optional header.

    All ``**attrs`` are forwarded to the overlay ``<div>``.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        open: bool = False,
        title: str | None = None,
        close_on_escape: bool = True,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("role", "dialog")
        attrs.setdefault("aria-modal", "true")
        attrs.setdefault("class_", "miki-modal")
        if title:
            attrs.setdefault("aria-label", title)
        if open:
            attrs.setdefault("data-open", "true")
        if close_on_escape:
            attrs.setdefault("data-close-on-escape", "true")

        panel = Div(*children, class_="miki-modal-panel")
        overlay = Div(panel, class_="miki-modal-overlay")
        super().__init__(overlay, **attrs)
        self._open = open

    @property
    def open(self) -> bool:
        return self._open

    @open.setter
    def open(self, value: bool) -> None:
        self._open = value
        if value:
            self.attrs.setdefault("data-open", "true")
        else:
            self.attrs.pop("data-open", None)
