"""Button components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Button(Component):
    tag = "button"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "button")
        super().__init__(*children, **attrs)


class SubmitButton(Button):
    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs["type"] = "submit"
        super().__init__(*children, **attrs)
