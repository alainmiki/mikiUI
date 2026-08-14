"""Input components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Input(Component):
    tag = "input"


class Textarea(Component):
    tag = "textarea"


class Checkbox(Input):
    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "checkbox")
        super().__init__(*children, **attrs)


class Radio(Input):
    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "radio")
        super().__init__(*children, **attrs)


class Slider(Input):
    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "range")
        super().__init__(*children, **attrs)
