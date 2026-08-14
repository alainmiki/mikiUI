"""Input components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Input(Component):
    """A styled ``<input>`` element.

    Accepts ``variant`` (``"default"`` or ``"filled"``) and ``size`` (``"sm"``,
    ``"md"``, ``"lg"``) in addition to standard input attributes.  All ``**attrs``
    are forwarded, so HTMX, ARIA, and arbitrary CSS classes work transparently.
    """

    tag = "input"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        variant = attrs.pop("variant", "default")
        size = attrs.pop("size", "md")
        classes = self._default_classes(variant, size)
        user_classes = attrs.pop("class_", "")
        attrs["class_"] = f"{classes} {user_classes}".strip()
        super().__init__(*children, **attrs)

    @staticmethod
    def _default_classes(variant: str, size: str) -> str:
        base = "miki-input"
        if variant == "filled":
            base += " miki-input-filled"
        if size == "sm":
            base += " miki-input-sm"
        elif size == "lg":
            base += " miki-input-lg"
        return base


class Textarea(Component):
    """A styled ``<textarea>`` element."""

    tag = "textarea"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-input")
        if attrs.get("rows") is None:
            attrs["rows"] = 4
        super().__init__(*children, **attrs)


class Checkbox(Input):
    """A checkbox input (defaults to ``type="checkbox"``)."""

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "checkbox")
        attrs.setdefault("class_", "miki-checkbox")
        user_classes = attrs.pop("class_", "")
        # Prepend miki-checkbox if user provided extra classes
        attrs["class_"] = f"miki-checkbox {user_classes}".strip() if user_classes else "miki-checkbox"
        super().__init__(*children, **attrs)


class Radio(Input):
    """A radio button input (defaults to ``type="radio"``)."""

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "radio")
        attrs.setdefault("class_", "miki-radio")
        super().__init__(*children, **attrs)


class Slider(Input):
    """A range slider input (defaults to ``type="range"``)."""

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "range")
        attrs.setdefault("class_", "miki-slider")
        super().__init__(*children, **attrs)
