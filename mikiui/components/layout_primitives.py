"""Layout primitive components: Column, Row, Stack, Spacer, Divider, Shape."""

from __future__ import annotations

from typing import Any

from .base import Component


class Column(Component):
    """A flex column container.

    :param children: Child elements.
    :param gap: Gap between children (CSS value, e.g. ``"1rem"``).
    :param align: CSS align-items value (``"stretch"``, ``"flex-start"``,
                  ``"flex-end"``, ``"center"``, ``"baseline"``).
    :param justify: CSS justify-content value.
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        gap: str = "",
        align: str = "",
        justify: str = "",
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-column"]
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))

        style_parts: list[str] = ["display: flex", "flex-direction: column"]
        if gap:
            style_parts.append(f"gap: {gap}")
        if align:
            style_parts.append(f"align-items: {align}")
        if justify:
            style_parts.append(f"justify-content: {justify}")

        existing = attrs.get("style", "")
        style = "; ".join(style_parts)
        if existing:
            style = f"{style}; {existing}"
        attrs.setdefault("style", style)
        super().__init__(*children, **attrs)


class Row(Component):
    """A flex row container.

    :param children: Child elements.
    :param gap: Gap between children (CSS value).
    :param align: CSS align-items value.
    :param justify: CSS justify-content value.
    :param wrap: If ``True``, allow children to wrap.
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        gap: str = "",
        align: str = "",
        justify: str = "",
        wrap: bool = False,
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-row"]
        if wrap:
            classes.append("miki-row-wrap")
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))

        style_parts: list[str] = ["display: flex", "flex-direction: row"]
        if gap:
            style_parts.append(f"gap: {gap}")
        if align:
            style_parts.append(f"align-items: {align}")
        if justify:
            style_parts.append(f"justify-content: {justify}")
        if wrap:
            style_parts.append("flex-wrap: wrap")

        existing = attrs.get("style", "")
        style = "; ".join(style_parts)
        if existing:
            style = f"{style}; {existing}"
        attrs.setdefault("style", style)
        super().__init__(*children, **attrs)


class Stack(Component):
    """A vertical stack with optional gap.

    Equivalent to a ``Column`` with sensible defaults.

    :param children: Child elements.
    :param gap: Gap between children.
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        gap: str = "0.5rem",
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-stack"]
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        attrs.setdefault("role", "group")
        attrs.setdefault("aria-label", "Stack")
        attrs.setdefault("style", f"display: flex; flex-direction: column; gap: {gap};")
        super().__init__(*children, **attrs)


class Spacer(Component):
    """A flexible spacer that expands to fill available space.

    :param size: CSS flex-grow value (default ``"1"``).
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        size: str = "1",
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-spacer"]
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        attrs.setdefault("style", f"flex: {size} 1 auto;")
        super().__init__(**attrs)


class Divider(Component):
    """A divider line.

    :param orientation: ``"horizontal"`` (default) or ``"vertical"``.
    :param label: Optional label text rendered in the center (horizontal only).
    :param class_: Extra CSS classes.
    """

    tag = "hr"

    def __init__(
        self,
        orientation: str = "horizontal",
        label: str | None = None,
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-divider"]
        if orientation == "vertical":
            classes.append("miki-divider-vertical")
        if label:
            classes.append("miki-divider-with-label")
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))

        style_parts: list[str] = []
        if orientation == "vertical":
            style_parts = ["width: 1px", "height: 100%", "border: none",
                           "border-left: 1px solid var(--miki-border)"]
        else:
            style_parts = ["border: none", "border-top: 1px solid var(--miki-border)",
                           "margin: 0.5rem 0"]

        if label:
            style_parts.append("display: flex")
            style_parts.append("align-items: center")

        existing = attrs.get("style", "")
        style = "; ".join(style_parts)
        if existing:
            style = f"{style}; {existing}"
        attrs.setdefault("style", style)

        if label:
            attrs.setdefault("role", "separator")
        super().__init__(**attrs)


class Shape(Component):
    """A shape wrapper with border-radius variants.

    :param children: Content to wrap.
    :param variant: ``"rounded"``, ``"circle"``, ``"pill"``, ``"square"``,
                    ``"none"``.
    :param size: CSS size value (e.g. ``"3rem"``).
    :param background: Optional background color.
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        variant: str = "rounded",
        size: str = "",
        background: str = "",
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-shape", f"miki-shape-{variant}"]
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))

        style_parts: list[str] = []
        if size:
            style_parts.append(f"width: {size}")
            style_parts.append(f"height: {size}")
        if background:
            style_parts.append(f"background: {background}")

        existing = attrs.get("style", "")
        style = "; ".join(style_parts)
        if existing:
            style = f"{style}; {existing}"
        if style:
            attrs.setdefault("style", style)
        super().__init__(*children, **attrs)
