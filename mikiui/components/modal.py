"""Modal component (custom overlay built from a ``<div>``).

This is the JS-driven, dependency-free version of Modal.  It no longer relies
on Alpine.js — ``miki_ui.js`` handles show/hide, overlay click, ESC close,
and close buttons via ``data-miki-*`` attributes.
"""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import Div


class Modal(Component):
    """A modal dialog: a fixed overlay ``<div>`` containing a content panel.

    Use ``open`` to control visibility.  Visibility is toggled client-side
    by ``miki_ui.js`` (no Alpine required).  All interactive behaviors —
    overlay click, ESC key, close button — are data-attribute-driven.

    Parameters
    ----------
    *children : Modal body content.
    open : bool
        Initial visibility (default: False).
    title : str | None
        Optional header title (adds ``aria-label`` and an ``aria-labelledby``
        reference, plus a title element).
    close_on_overlay : bool
        Close when clicking outside the panel on the backdrop.
    close_on_escape : bool
        Close on ``Escape`` key.
    size : str
        Size variant: xs, sm, md (default), lg, xl, fullscreen.
    **attrs : Additional HTML attributes forwarded to the overlay.

    Example
    -------
    >>> Modal(
    ...     P("Are you sure you want to continue?"),
    ...     title="Confirm",
    ...     open=True,
    ...     size="sm",
    ... )
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        open: bool = False,
        title: str | None = None,
        close_on_overlay: bool = True,
        close_on_escape: bool = True,
        size: str = "md",
        **attrs: Any,
    ) -> None:
        if size not in ("xs", "sm", "md", "lg", "xl", "fullscreen"):
            size = "md"

        attrs.setdefault("role", "dialog")
        attrs.setdefault("aria-modal", "true")
        attrs.setdefault("aria-hidden", str(not open).lower())
        attrs.setdefault("class_", f"miki-modal miki-modal-{size}")
        attrs.setdefault("data-miki-modal", "true")
        attrs.setdefault("data-miki-modal-open", str(open).lower())
        attrs.setdefault("data-miki-close-on-overlay", str(close_on_overlay).lower())
        attrs.setdefault("data-miki-close-on-escape", str(close_on_escape).lower())

        if title:
            attrs.setdefault("aria-labelledby", f"{title}-modal-title")

        panel_children: list[Any] = list(children)
        if title:
            panel_children.insert(
                0,
                Div(title, class_="miki-modal-title", id=f"{title}-modal-title"),
            )

        # Add a close button if none is present in children
        has_close = any(
            "data-miki-modal-close" in str(getattr(c, "attrs", {}))
            for c in panel_children
        )
        if not has_close:
            from .button import Button
            panel_children.insert(
                1 if title else 0,
                Button(
                    "×",
                    type="button",
                    class_="miki-modal-close-btn",
                    role="button",
                    aria_label="Close modal",
                    **{"data-miki-modal-close": "true"},
                ),
            )

        panel = Div(*panel_children, class_="miki-modal-panel")
        overlay = Div(panel, class_="miki-modal-overlay")
        super().__init__(overlay, **attrs)

    @property
    def open(self) -> bool:
        return self.attrs.get("data-miki-modal-open") == "true"

    @open.setter
    def open(self, value: bool) -> None:
        self.attrs["data-miki-modal-open"] = str(value).lower()
        self.attrs["aria-hidden"] = str(not value).lower()
