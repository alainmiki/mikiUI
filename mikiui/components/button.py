"""Button components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Button(Component):
    """A styled ``<button>`` element.

    Default variant is ``primary`` (solid accent).  Pass ``variant="ghost"``
    for an outline/ghost style, or ``size="sm"``/``"lg"`` for compact/large.

    Any extra ``**attrs`` are forwarded to the underlying element, so users can
    pass arbitrary HTMX attributes (``hx_post``, ``hx_get``, etc.), ARIA
    attributes, or raw Tailwind/DaisyUI classes via ``class_``.
    """

    tag = "button"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "button")
        variant = attrs.pop("variant", "primary")
        size = attrs.pop("size", "md")

        classes = self._default_classes(variant, size)
        user_classes = attrs.pop("class_", "")
        attrs["class_"] = f"{classes} {user_classes}".strip()

        super().__init__(*children, **attrs)

    @staticmethod
    def _default_classes(variant: str, size: str) -> str:
        base = "miki-btn"
        if size == "sm":
            base += " miki-btn-sm"
        elif size == "lg":
            base += " miki-btn-lg"

        if variant == "primary":
            base += " miki-btn-primary"
        elif variant == "ghost":
            base += " miki-btn-ghost"
        elif variant == "secondary":
            base += " miki-btn-secondary"
        return base


class SubmitButton(Button):
    """A submit button — defaults to ``type="submit"`` and ``variant="primary"``."""

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs["type"] = "submit"
        super().__init__(*children, **attrs)
