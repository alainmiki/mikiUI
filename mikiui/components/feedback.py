"""Feedback primitive components: ActivityIndicator, Pressable."""

from __future__ import annotations

from typing import Any

from .base import Component


class ActivityIndicator(Component):
    """A loading spinner / activity indicator.

    Material Design / Cupertino style indeterminate spinner, with optional
    determinate progress mode.

    :param size: ``"sm"`` (16px), ``"md"`` (24px, default), or ``"lg"`` (40px).
    :param label: Optional accessible label.
    :param progress: Optional determinate progress value ``0.0`` – ``1.0``.
                     When provided, renders a determinate circular indicator.
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        size: str = "md",
        label: str | None = None,
        progress: float | None = None,
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-activity-indicator"]
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        attrs.setdefault("role", "status")

        if label:
            attrs.setdefault("aria-label", label)
        else:
            attrs.setdefault("aria-label", "Loading")

        style_parts: list[str] = []
        if size == "sm":
            style_parts.append("width: 1rem; height: 1rem")
        elif size == "md":
            style_parts.append("width: 1.5rem; height: 1.5rem")
        elif size == "lg":
            style_parts.append("width: 2.5rem; height: 2.5rem")

        if progress is not None:
            style_parts.append(f"--miki-progress: {max(0.0, min(1.0, progress))}")

        existing = attrs.get("style", "")
        style = "; ".join(style_parts)
        if existing:
            style = f"{style}; {existing}"
        if style:
            attrs.setdefault("style", style)

        if progress is not None:
            attrs.setdefault("data-miki-activity-determinate", "true")

        super().__init__(**attrs)


class Pressable(Component):
    """A pressable container with visual feedback.

    Renders a ``<div>`` with ``data-miki-pressable="true"``. JS adds/removes
    ``.miki-press-active`` on pointer down/up. Supports hover and focus
    states natively via CSS.

    :param children: Content.
    :param feedback: ``"opacity"`` or ``"scale"``.
    :param disabled: If ``True``, render in disabled state.
    :param class_: Extra CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        feedback: str = "opacity",
        disabled: bool = False,
        class_: str = "",
        **attrs: Any,
    ) -> None:
        classes = ["miki-pressable", f"miki-pressable-{feedback}"]
        if disabled:
            classes.append("miki-press-disabled")
        if class_:
            classes.append(class_)
        attrs.setdefault("class_", " ".join(classes))
        attrs.setdefault("data-miki-pressable", "true")
        if not disabled:
            attrs.setdefault("tabindex", "0")
        attrs.setdefault("role", "button")

        if disabled:
            attrs.setdefault("aria-disabled", "true")
            attrs.setdefault("tabindex", "-1")

        super().__init__(*children, **attrs)
