"""Dialog and disclosure components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Dialog(Component):
    """A styled ``<dialog>`` element.

    ``open`` controls the ``open`` attribute.  Pass ``class_`` for extra classes.
    """

    tag = "dialog"

    def __init__(self, *children: Any, open: bool = False, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-dialog")
        if open:
            attrs["open"] = True
        super().__init__(*children, **attrs)


class Details(Component):
    """A styled ``<details>`` element for disclosure."""

    tag = "details"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-details")
        super().__init__(*children, **attrs)


class Summary(Component):
    """A styled ``<summary>`` element."""

    tag = "summary"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-summary")
        super().__init__(*children, **attrs)
