"""Dialog and disclosure components with proper click handling.

These components work with or without Alpine.js - they use plain DOM
events for maximum compatibility and reliability.

Features:
- click OUTSIDE to close (overlay)
- ESC key closing
- fade animations
- ARIA-compliant roles
- size variants
"""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import Div


class Dialog(Component):
    """A styled dialog with click-to-close overlay and ESC support.

    Uses native <dialog> element with fallback JavaScript for close behavior.

    Example
    -------
    >>> Dialog(
    ...     Button("Close", onclick="mikiCloseDialog(this)"),
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

        if title:
            attrs.setdefault("aria-label", title)

        if open:
            attrs["open"] = True

        children_list = list(children)
        if title:
            children_list.insert(0, Div(title, class_="miki-dialog-title"))

        if close_on_overlay:
            overlay = Div(
                class_="miki-dialog-overlay",
                onclick="event.target === this && this.closest('dialog').close()",
            )
            children_list.insert(0, overlay)

        if close_on_escape:
            attrs["data_close_on_escape"] = "true"

        super().__init__(*children_list, **attrs)

    @property
    def open(self) -> bool:
        return "open" in self.attrs or "data-open" in self.attrs.get("class", "")

    @open.setter
    def open(self, value: bool) -> None:
        if value:
            self.attrs["open"] = True
        else:
            self.attrs.pop("open", None)


class Modal(Component):
    """A modal overlay dialog.

    Uses a div overlay that can be toggled with Alpine.js or natively.

    Example
    -------
    >>> Modal(
    ...     H2("Title"),
    ...     P("Content"),
    ...     open=True,
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
        attrs.setdefault("aria_label", title or "Modal")

        attrs.setdefault("x_data", f"{{show:{str(open).lower()}}}")
        attrs.setdefault("x_show", "show")
        attrs.setdefault("x_transition", "enter: ease-out duration-200; leave: ease-in duration-150")

        attrs.setdefault("class", f"miki-modal miki-modal-{size}")

        if open:
            attrs["data-open"] = "true"

        overlay_attrs = {}
        if close_on_overlay:
            overlay_attrs["x_on:click"] = "event.target === $el && (show=false)"
        else:
            overlay_attrs["x_on:click"] = "event.stopPropagation()"

        if close_on_escape:
            attrs["x_on:keydown.escape"] = "show = false"

        panel_children = list(children)
        if title:
            panel_children.insert(0, Div(title, class_="miki-modal-title"))

        panel = Div(
            *panel_children,
            class_="miki-modal-panel",
        )
        overlay = Div(panel, class_="miki-modal-overlay", **overlay_attrs)

        super().__init__(overlay, **attrs)


class DialogTitle(Div):
    tag = "div"


class DialogBody(Div):
    tag = "div"


class DialogFooter(Div):
    tag = "div"


class Details(Component):
    """A styled details/summary disclosure element.

    Uses native <details> for accessibility with enhanced styling.
    """

    tag = "details"

    def __init__(self, *children: Any, open: bool = False, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-details miki-details-collapsible")
        if open:
            attrs["open"] = True

        attrs.setdefault("x_data", f"{{opened:{str(open).lower()}}}")

        super().__init__(*children, **attrs)

    @property
    def open(self) -> bool:
        return "open" in self.attrs


class Summary(Component):
    """A styled summary element for details disclosure."""

    tag = "summary"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-summary")
        attrs.setdefault("role", "button")
        attrs.setdefault("tabindex", "0")
        attrs["x_on_click"] = "$el.closest('details').open = !($el.closest('details').open)"
        attrs["x_on_keydown.enter"] = "$el.click()"
        attrs["x_on_keydown.space"] = "$el.click(); event.preventDefault()"
        super().__init__(*children, **attrs)