"""PropertyGrid widget: an editable key/value table."""

from __future__ import annotations

from typing import Any

from ..components import Input, Td, Tr, Tbody, Thead
from ..components.base import Component


class PropertyGrid(Component):
    """Render an editable property table (name + input per row).

    :param items: mapping of property name to value.
    """

    tag = "table"

    def __init__(self, items: dict[str, Any], **attrs: Any) -> None:
        attrs.setdefault("class", "miki-property-grid")
        attrs.setdefault("role", "grid")
        thead = Thead(Tr(Td("Property"), Td("Value"), role="row"))
        body_rows = [
            Tr(
                Td(key, role="gridcell"),
                Td(Input(name=key, value=value), role="gridcell"),
                role="row",
            )
            for key, value in items.items()
        ]
        tbody = Tbody(*body_rows)
        super().__init__(thead, tbody, **attrs)
