"""Form components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Form(Component):
    """A styled ``<form>`` element.

    ``layout`` can be ``"vertical"`` (default, stacked labels) or ``"inline"``
    (horizontal, compact).  All ``**attrs`` are forwarded.
    """

    tag = "form"

    def __init__(self, *children: Any, layout: str = "vertical", novalidate: bool = True, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-form-inline" if layout == "inline" else "miki-form")
        if novalidate:
            attrs.setdefault("novalidate", True)
        super().__init__(*children, **attrs)


class Label(Component):
    """A styled ``<label>`` element."""

    tag = "label"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-label")
        super().__init__(*children, **attrs)


class Optgroup(Component):
    """An ``<optgroup>`` element."""

    tag = "optgroup"


class Fieldset(Component):
    """A styled ``<fieldset>`` element."""

    tag = "fieldset"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-fieldset")
        super().__init__(*children, **attrs)


class Legend(Component):
    """A styled ``<legend>`` element."""

    tag = "legend"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-legend")
        super().__init__(*children, **attrs)
