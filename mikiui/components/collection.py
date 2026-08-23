"""Data/collection components: Chip, LazyGrid, VirtualList, ScrollView."""

from __future__ import annotations

from typing import Any

from .base import Component
from .button import Button
from .html import Div, Img, Span


class Chip(Component):
    """A compact selectable chip.

    Selection state is managed client-side by JS. Use ``selected=True`` for
    the default active state.

    :param children: Chip content.
    :param selected: If ``True``, chip starts in selected state.
    :param removable: If ``True``, show a remove button.
    :param avatar: Optional image URL for leading avatar.
    :param icon: Optional icon name for leading icon.
    :param class_: Extra CSS classes.
    """

    tag = "span"

    def __init__(
        self,
        *children: Any,
        selected: bool = False,
        removable: bool = False,
        avatar: str | None = None,
        icon: str | None = None,
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-chip"]
        if selected:
            classes.append("miki-chip-selected")
        if removable:
            classes.append("miki-chip-removable")
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        attrs.setdefault("data-miki-chip", "true")
        attrs.setdefault("role", "option")
        attrs.setdefault("aria-selected", "true" if selected else "false")
        attrs.setdefault("tabindex", "0")

        parts: list[Any] = []
        if avatar:
            parts.append(
                Img(
                    src=avatar,
                    class_="miki-chip-avatar",
                    alt="",
                )
            )
        elif icon:
            from ..widgets.icon import Icon
            parts.append(Icon(icon, class_="miki-chip-icon"))

        if children:
            parts.append(
                Span(*children, class_="miki-chip-content")
            )

        if removable:
            parts.append(
                Button(
                    "×",
                    class_="miki-chip-remove",
                    aria_label="Remove",
                    data_miki_chip_remove="true",
                )
            )

        super().__init__(*parts, **attrs)


class LazyGrid(Component):
    """A lazy-loading grid that defers off-screen items.

    Items should be wrapped in a container with class ``miki-lazy-item``.
    JS uses IntersectionObserver to hydrate them when they enter the viewport.

    :param children: Grid items.
    :param columns: Number of columns (default ``"1"``).
    :param gap: Gap between items.
    :param on_load_more: Optional callback name invoked when near the end
                         for infinite-scroll patterns.
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        columns: str = "1",
        gap: str = "1rem",
        on_load_more: str | None = None,
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-lazy-grid"]
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        attrs.setdefault("data-miki-lazy-grid", "true")
        attrs.setdefault("data-miki-columns", columns)
        attrs.setdefault("style", f"grid-template-columns: repeat({columns}, 1fr); gap: {gap};")
        if on_load_more:
            attrs.setdefault("data-miki-lazy-load-more", on_load_more)
        super().__init__(*children, **attrs)


class VirtualList(Component):
    """A virtualized scrollable list.

    JS windowing renders only visible items. All items must have the same
    height for deterministic virtualization.

    :param children: List items (all same height).
    :param item_height: Height of each item in pixels.
    :param overscan: Extra items to render above/below viewport.
    :param on_scroll: Optional callback name invoked on scroll.
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        item_height: int = 48,
        overscan: int = 4,
        on_scroll: str | None = None,
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-virtual-list"]
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        attrs.setdefault("data-miki-virtual-list", "true")
        attrs.setdefault("data-miki-item-height", str(item_height))
        attrs.setdefault("data-miki-overscan", str(overscan))
        attrs.setdefault("role", "list")
        attrs.setdefault("style", "height: 400px; overflow: auto; position: relative;")
        if on_scroll:
            attrs.setdefault("data-miki-virtual-list-on-scroll", on_scroll)
        super().__init__(*children, **attrs)


class ScrollView(Component):
    """A scrollable container.

    :param children: Scrollable content.
    :param orientation: ``"vertical"`` (default) or ``"horizontal"``.
    :param on_scroll: Optional callback name invoked on scroll.
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        orientation: str = "vertical",
        on_scroll: str | None = None,
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-scrollview"]
        if orientation == "horizontal":
            classes.append("miki-scrollview-horizontal")
        else:
            classes.append("miki-scrollview-vertical")
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        if orientation == "horizontal":
            attrs.setdefault("style", "overflow-x: auto; overflow-y: hidden; -webkit-overflow-scrolling: touch;")
        else:
            attrs.setdefault("style", "overflow-y: auto; overflow-x: hidden; -webkit-overflow-scrolling: touch;")
        if on_scroll:
            attrs.setdefault("data-miki-scrollview-on-scroll", on_scroll)
        super().__init__(*children, **attrs)
