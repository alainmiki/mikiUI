"""DataGrid widget: a paginated/scrollable table of columns and rows."""

from __future__ import annotations

from typing import Any

from ..components import Td, Th, Tr, Tbody, Thead
from ..components.base import Component
from ..engine import _


class DataGrid(Component):
    """Render tabular data as an accessible ``Table``.

    :param columns: list of column header labels.
    :param rows: list of rows, each a list of cell values.
    :param pagination: when True, slice rows by ``page``/``page_size``.
    :param page: zero-based page index (used when ``pagination`` is True).
    :param page_size: rows shown per page (used when ``pagination`` is True).
    """

    tag = "table"

    def __init__(
        self,
        columns: list[str],
        rows: list[list],
        pagination: bool = False,
        page: int = 0,
        page_size: int = 10,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("role", "grid")
        attrs.setdefault("class", "miki-datagrid")
        self.columns = columns
        self.rows = rows
        self.pagination = pagination
        self.page = page
        self.page_size = page_size

        thead = Thead(Tr(*[Th(_(f"col_{c}", str(c))) for c in columns]))
        visible = rows
        if pagination:
            start = page * page_size
            visible = rows[start : start + page_size]
        body_rows = [Tr(*[Td(cell) for cell in row], role="row") for row in visible]
        tbody = Tbody(*body_rows)
        super().__init__(thead, tbody, **attrs)
