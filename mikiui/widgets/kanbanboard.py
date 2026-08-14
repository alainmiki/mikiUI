"""KanbanBoard widget: columns of item lists."""

from __future__ import annotations

from typing import Any

from ..components import Div, H3, ListView
from ..components.base import Component


class KanbanBoard(Component):
    """Render a kanban board from a mapping of column -> items.

    :param columns: dict mapping column title to a list of item labels.
    """

    tag = "div"

    def __init__(self, columns: dict[str, list], **attrs: Any) -> None:
        attrs.setdefault("class", "miki-kanban")
        attrs.setdefault("role", "list")
        column_nodes = []
        for title, items in columns.items():
            column_nodes.append(
                Div(
                    H3(title),
                    ListView(items),
                    class_="miki-kanban-column",
                    role="group",
                    aria_label=title,
                )
            )
        super().__init__(*column_nodes, **attrs)
