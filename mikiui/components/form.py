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

    def __init__(self, *children: Any, layout: str = "vertical", **attrs: Any) -> None:
        if layout == "inline":
            attrs.setdefault("class_", "miki-form-inline")
        else:
            attrs.setdefault("class_", "miki-form")
        super().__init__(*children, **attrs)


class Label(Component):
    """A styled ``<label>`` element."""

    tag = "label"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-label")
        super().__init__(*children, **attrs)


class Select(Component):
    """A styled ``<select>`` element."""

    tag = "select"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-select")
        super().__init__(*children, **attrs)


class Option(Component):
    """An ``<option>`` element."""

    tag = "option"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-option")
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
