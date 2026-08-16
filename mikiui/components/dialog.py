"""Dialog, Modal, and disclosure components.

These components work fully **without** Alpine.js.  All interactivity is
handled by ``miki_ui.js`` via ``data-miki-*`` attributes.  The Alpine
``x_on_*`` / ``x_data`` directives are emitted as progressive-enhancement
fallbacks only — the JS runtime ignores them but is the primary controller.

Features:
- Click OUTSIDE to close (overlay / backdrop)
- ESC key closing
- Fade / slide animations (CSS)
- ARIA-compliant roles and properties
- Size variants (xs, sm, md, lg, xl, fullscreen)
- Native <dialog> polyfill for non-supporting browsers
"""

from __future__ import annotations

from typing import Any

from .base import Component
from .button import Button
from .html import Div


class Dialog(Component):
    """A styled dialog using the native ``<dialog>`` element with JS polyfill.

    The dialog is auto-wired by ``miki_ui.js``: overlay click, ESC key,
    and close buttons all work without Alpine.

    Example
    -------
    >>> Dialog(
    ...     Button("Close", onclick="mikiDialog.close(this.closest('dialog'))"),
    ...     open=True,
    ...     title="Confirmation",
    ... )
    """

    tag = "dialog"

    def __init__(
        self,
        *children: Any,
        open: bool = False,
        title: str | None = None,
        size: str = "md",
        close_on_overlay: bool = True,
        close_on_escape: bool = True,
        **attrs: Any,
    ) -> None:
        if size not in ("xs", "sm", "md", "lg", "xl", "fullscreen"):
            size = "md"

        attrs.setdefault("class", f"miki-dialog miki-dialog-{size}")
        attrs.setdefault("role", "dialog")
        attrs.setdefault("aria-modal", "true")
        attrs.setdefault("data-miki-dialog", "true")
        attrs.setdefault("data-miki-dialog-close-on-overlay", str(close_on_overlay).lower())
        attrs.setdefault("data-miki-dialog-close-on-escape", str(close_on_escape).lower())

        if title:
            attrs.setdefault("aria-labelledby", f"{title}-dialog-title")
            attrs.setdefault("aria-label", title)

        if open:
            attrs["open"] = True

        children_list: list[Any] = list(children)

        if title:
            children_list.insert(0, Div(title, class_="miki-dialog-title", id=f"{title}-dialog-title"))

        if close_on_overlay:
            overlay = Div(
                class_="miki-dialog-overlay",
                **{"data-miki-dialog-close": "true"}
            )
            children_list.insert(0, overlay)

        # Add a default close button if none provided in children
        has_close = any(
            "data-miki-dialog-close" in str(getattr(c, "attrs", {}))
            for c in children_list
        )
        if not has_close:
            children_list.insert(
                1 if title else 0,
                Button(
                    "×",
                    type="button",
                    class_="miki-dialog-close-btn",
                    role="button",
                    aria_label="Close dialog",
                    **{"data-miki-dialog-close": "true"},
                )
            )

        super().__init__(*children_list, **attrs)

    @property
    def open(self) -> bool:
        return "open" in self.attrs or self.attrs.get("data-open") == "true"

    @open.setter
    def open(self, value: bool) -> None:
        if value:
            self.attrs["open"] = True
        else:
            self.attrs.pop("open", None)
            self.attrs.pop("data-open", None)


class Modal(Component):
    """A modal overlay dialog (custom ``<div>`` with backdrop).

    Visibility is toggled client-side by ``miki_ui.js``.  No Alpine required.

    Parameters
    ----------
    *children : Modal content.
    open : bool
        Initial visibility.
    title : str | None
        Optional header title (adds ``aria-label`` and a title element).
    close_on_overlay : bool
        Close when clicking the backdrop.
    close_on_escape : bool
        Close on ESC key.
    size : str
        Size variant: xs, sm, md, lg, xl, fullscreen.
    **attrs : Additional HTML attributes.

    Example
    -------
    >>> Modal(
    ...     P("Content"),
    ...     open=True,
    ...     title="My Modal",
    ...     size="md",
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
        if title:
            attrs.setdefault("aria-label", title)
        attrs.setdefault("data-miki-close-on-overlay", str(close_on_overlay).lower())
        attrs.setdefault("data-miki-close-on-escape", str(close_on_escape).lower())

        panel_children: list[Any] = list(children)
        if title:
            panel_children.insert(0, Div(title, class_="miki-modal-title", id=f"{title}-modal-title"))
            attrs.setdefault("aria-labelledby", f"{title}-modal-title")

        # Add a close button if none is present
        has_close = any(
            "data-miki-modal-close" in str(getattr(c, "attrs", {}))
            for c in panel_children
        )
        if not has_close:
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


class DialogTitle(Div):
    """Title element for dialogs (maps to ``<div>`` with styling)."""

    tag = "div"


class DialogBody(Div):
    """Body content container for dialogs."""

    tag = "div"


class DialogFooter(Div):
    """Footer content container for dialogs (actions, buttons)."""

    tag = "div"


class Details(Component):
    """A styled ``<details>`` / ``<summary>`` disclosure element.

    Uses native ``<details>`` for accessibility.  No JavaScript required.
    """

    tag = "details"

    def __init__(self, *children: Any, open: bool = False, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-details miki-details-collapsible")
        if open:
            attrs["open"] = True
        super().__init__(*children, **attrs)

    @property
    def open(self) -> bool:
        return "open" in self.attrs


class Summary(Component):
    """A styled ``<summary>`` element for details disclosure."""

    tag = "summary"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-summary")
        attrs.setdefault("role", "button")
        attrs.setdefault("tabindex", "0")
        super().__init__(*children, **attrs)