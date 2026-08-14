"""Table components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Table(Component):
    """A styled ``<table>`` element.

    ``variant`` can be ``"default"`` (bordered, header shaded) or ``"striped"``
    (alternating row backgrounds).  Pass ``class_`` to add extra Tailwind/DaisyUI
    classes.
    """

    tag = "table"

    def __init__(self, *children: Any, variant: str = "default", **attrs: Any) -> None:
        classes = "miki-table"
        if variant == "striped":
            classes += " miki-table-striped"
        user_classes = attrs.pop("class_", "")
        attrs["class_"] = f"{classes} {user_classes}".strip()
        super().__init__(*children, **attrs)


class Caption(Component):
    """A ``<caption>`` element."""

    tag = "caption"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-caption")
        super().__init__(*children, **attrs)


class Thead(Component):
    tag = "thead"


class Tbody(Component):
    tag = "tbody"


class Tfoot(Component):
    tag = "tfoot"


class Tr(Component):
    tag = "tr"


class Th(Component):
    """A styled ``<th>`` element."""

    tag = "th"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-th")
        super().__init__(*children, **attrs)


class Td(Component):
    """A styled ``<td>`` element."""

    tag = "td"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-td")
        super().__init__(*children, **attrs)
