"""Dialog and disclosure components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Dialog(Component):
    tag = "dialog"

    def __init__(self, *children: Any, open: bool = False, **attrs: Any) -> None:
        if open:
            attrs["open"] = True
        super().__init__(*children, **attrs)


class Details(Component):
    tag = "details"


class Summary(Component):
    tag = "summary"
