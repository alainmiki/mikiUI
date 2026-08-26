"""Surface components: SafeAreaView, BottomSheet, BottomNavigation, FloatingActionButton."""

from __future__ import annotations

from typing import Any

from .base import Component
from .button import Button
from .html import Div, Span


class SafeAreaView(Component):
    """A container that applies safe-area insets.

    :param children: Content.
    :param edges: ``"all"``, ``"top"``, ``"bottom"``, ``"left"``, ``"right"``,
                  or comma-separated like ``"top,bottom"``.
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        edges: str = "all",
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-safe-area"]
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))

        inset_map = {
            "top": "env(safe-area-inset-top, 0px)",
            "bottom": "env(safe-area-inset-bottom, 0px)",
            "left": "env(safe-area-inset-left, 0px)",
            "right": "env(safe-area-inset-right, 0px)",
        }

        parts = []
        if edges == "all":
            parts = [
                f"padding-top: {inset_map['top']}",
                f"padding-bottom: {inset_map['bottom']}",
                f"padding-left: {inset_map['left']}",
                f"padding-right: {inset_map['right']}",
            ]
        else:
            for edge in [e.strip() for e in edges.split(",") if e.strip()]:
                if edge in inset_map:
                    parts.append(f"padding-{edge}: {inset_map[edge]}")

        style = "; ".join(parts)
        existing = attrs.get("style", "")
        attrs.setdefault("style", f"{style}; {existing}" if existing else style)
        super().__init__(*children, **attrs)


class BottomSheet(Component):
    """A bottom sheet overlay that slides up from the bottom of the screen.

    State is JS-only. Open/close via :func:`mikiBottomSheet.open` /
    :func:`mikiBottomSheet.close` or by setting
    ``data-miki-bottom-sheet-open="true"`` on the container.

     :param children: Sheet content.
    :param title: Optional title rendered in the header.
    :param closable: If ``True``, show close button and allow ESC/backdrop close.
    :param size: ``"sm"``, ``"md"``, ``"lg"``, or ``"full"``.
    :param on_open: Optional callback name invoked on open.
    :param on_close: Optional callback name invoked on close.
    :param class_: Extra CSS classes.

    Example::

        from mikiui.components import BottomSheet

        BottomSheet(
            P("Sheet content goes here"),
            title="My Sheet",
            size="md",
            on_close="handleSheetClose",
        )
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        title: str | None = None,
        closable: bool = True,
        size: str = "md",
        on_open: str | None = None,
        on_close: str | None = None,
        class_: str = "",
        **attrs: Any,
    ) -> None:
        if size not in ("sm", "md", "lg", "full"):
            raise ValueError(f"size must be 'sm', 'md', 'lg', or 'full', got {size!r}")
        classes = ["miki-bottom-sheet"]
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        attrs.setdefault("data-miki-bottom-sheet", "true")
        attrs.setdefault("data-miki-bottom-sheet-open", "false")
        attrs.setdefault("role", "dialog")
        attrs.setdefault("aria-modal", "true")
        attrs.setdefault("aria-hidden", "true")
        if title:
            attrs.setdefault("aria-label", title)
        if on_open:
            attrs.setdefault("data-miki-bottom-sheet-on-open", on_open)
        if on_close:
            attrs.setdefault("data-miki-bottom-sheet-on-close", on_close)

        header_parts: list[Any] = []
        if title:
            header_parts.append(
                Span(
                    title,
                    class_="miki-bottom-sheet-title",
                )
            )
        if closable:
            header_parts.append(
                Button(
                    "✕",
                    class_="miki-bottom-sheet-close",
                    aria_label="Close",
                    data_miki_bottom_sheet_close="true",
                )
            )

        header = Div(*header_parts, class_="miki-bottom-sheet-header") if header_parts else None
        drag_handle = Div(class_="miki-bottom-sheet-drag-handle")

        panel_children: list[Any] = [drag_handle]
        if header:
            panel_children.append(header)
        panel_children.extend(children)
        panel = Div(*panel_children, class_=f"miki-bottom-sheet-panel miki-bottom-sheet-{size}")

        backdrop = Div(
            class_="miki-bottom-sheet-backdrop",
            data_miki_bottom_sheet_backdrop="true",
        )

        super().__init__(backdrop, panel, **attrs)


class BottomNavigation(Component):
    """A bottom tab bar.

    State is HTMX-driven. Each item should be an ``<a>`` or ``<button>``
    with ``hx-get``/``hx-post`` pointing to a route that returns the updated
    navigation fragment. JS only handles visual active-state toggling and
    keyboard navigation.

    :param children: Navigation items (links/buttons with class
                     ``miki-bottom-nav-item``).
    :param active: Optional zero-based active item index.
    :param class_: Extra CSS classes.
    """

    tag = "nav"

    def __init__(
        self,
        *children: Any,
        active: int | None = None,
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-bottom-nav"]
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        attrs.setdefault("role", "tablist")
        attrs.setdefault("data-miki-bottom-nav", "true")
        if active is not None:
            attrs.setdefault("data-miki-active-index", str(active))
        super().__init__(*children, **attrs)


class FloatingActionButton(Component):
    """A floating action button.

    :param children: Icon/content.
    :param position: ``"bottom-right"``, ``"bottom-left"``, ``"top-right"``,
                     ``"top-left"``.
    :param extended: If ``True``, render wide variant with label.
    :param aria_label: Accessible label (required for icon-only buttons).
    :param class_: Extra CSS classes.
    """

    tag = "button"

    def __init__(
        self,
        *children: Any,
        position: str = "bottom-right",
        extended: bool = False,
        aria_label: str = "Action",
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-fab", f"miki-fab-{position}"]
        if extended:
            classes.append("miki-fab-extended")
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        attrs.setdefault("type", "button")
        attrs.setdefault("aria-label", aria_label)
        super().__init__(*children, **attrs)
