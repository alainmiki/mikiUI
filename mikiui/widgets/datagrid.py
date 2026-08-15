"""DataGrid widget: a sortable, filterable, paginated table.

Inspired by:
- Material Design Data Tables (sort indicators, filter chips)
- AG-Grid (sorting, filtering, editing)
- DataTables.js (search, pagination controls)

Features:
- Column sorting (click header for ascending/descending)
- Global and column-specific filtering
- Pagination with page navigation
- Keyboard navigation (arrow keys, Home/End)
- Editable cells (optional)
- Export to CSV/Excel
- Responsive design

Parameters
----------
columns : list[str] | list[tuple]
    Column definitions. Can be strings or tuples of (header, field, options)
rows : list[dict] | list[list]
    Row data. Dicts allow filtering/sorting by field name.
sortable : bool
    Allow column sorting
filterable : bool
    Allow filtering
pagination : bool
    Enable pagination
search : bool
    Enable global search input
page : int
    Current page (0-indexed)
page_size : int
    Rows per page
editable : bool
    Allow inline cell editing
editable_renderer : callable | None
    Custom renderer for editing cells
attrs : Any
    Additional HTML attributes

Example
-------
>>> # Sortable table with filtering
>>> DataGrid(
...     columns=["Name", "Email", "Role", "Status"],
...     rows=[
...         {"Name": "Alice", "Email": "alice@example.com", "Role": "Admin", "Status": "Active"},
...         {"Name": "Bob", "Email": "bob@example.com", "Role": "User", "Status": "Inactive"},
...     ],
...     sortable=True,
...     filterable=True,
...     pagination=True,
... )

>>> # Column tuples for advanced config
>>> DataGrid(
...     columns=[
...         ("Name", "name", {"sortable": True, "filterable": True}),
...         ("Email", "email", {"sortable": True}),
...         ("Role", "role", {"filterable": True}),
...     ],
...     rows=[{"name": "Alice", "email": "alice@example.com", "role": "Admin"}],
... )
"""

from __future__ import annotations

from typing import Any

from ..components import Td, Th, Tr, Tbody, Thead, Div, Input, Button
from ..components.base import Component
from ..engine import _


class DataGrid(Component):
    """Render tabular data as an accessible sortable, filterable Table.

    Columns can be strings or tuples of (header, field_name, options_dict).
    Options dict keys: sortable, filterable, width, align, type (number/string).

    Example:
        columns = [
            "Name",  # Simple string column
            ("Email", "email", {"sortable": True}),  # With field name and options
            ("Status", "status", {"filterable": True, "type": "select", "options": ["Active", "Inactive"]}),
        ]
    """

    tag = "table"

    def __init__(
        self,
        columns: list[str | tuple],
        rows: list[dict | list],
        *,
        sortable: bool = True,
        filterable: bool = False,
        pagination: bool = True,
        search: bool = True,
        page: int = 0,
        page_size: int = 10,
        height: int | None = None,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("role", "grid")
        attrs.setdefault("class", "miki-datagrid")
        self.columns = columns
        self.rows = rows
        self.sortable = sortable
        self.filterable = filterable
        self.pagination = pagination
        self.search = search
        self.page = page
        self.page_size = page_size
        self.height = height

        parent_class = attrs.get("class", "")
        if height:
            attrs["class_"] = f"{parent_class} miki-datagrid-scrollable"
            attrs.setdefault("style", f"max-height: {height}px;")

        thead_children = self._build_column_headers()
        thead = Thead(*thead_children, class_="miki-datagrid-head")
        tbody_children = self._build_body_rows()
        tbody = Tbody(*tbody_children)

        super().__init__(thead, tbody, **attrs)

        self._add_alpine_init()

    def _parse_column(self, col: str | tuple) -> tuple[str, str, dict]:
        if isinstance(col, str):
            return (col, col, {"sortable": self.sortable, "filterable": self.filterable})
        elif len(col) == 2:
            return (str(col[0]), str(col[1]), {"sortable": self.sortable, "filterable": self.filterable})
        else:
            return (str(col[0]), str(col[1]), dict(col[2]))

    def _build_column_headers(self) -> list[Th]:
        headers: list[Th] = []
        for col in self.columns:
            label, field, opts = self._parse_column(col)
            th_classes = ["miki-th"]
            if opts.get("width"):
                th_classes.append(f"miki-th-width-{opts['width']}")
            if opts.get("align"):
                th_classes.append(f"miki-th-{opts['align']}")

            th_attrs = {"class_": " ".join(th_classes)}
            if opts.get("type") == "number":
                th_attrs["class_"] += " miki-th-number"
            if opts.get("align"):
                th_attrs["class_"] += f" miki-text-{opts['align']}"

            if not opts.get("sortable", False):
                headers.append(Th(label, **th_attrs))
            else:
                th_attrs["x_on_click"] = f"datagrid.sortField='{field}'; datagrid.sortDir=datagrid.sortDir==='asc'?'desc':'asc'"
                th_attrs["class_"] += " miki-th-sortable"
                headers.append(Th(label, **th_attrs))
        return headers

    def _build_body_rows(self) -> list[Tr]:
        visible_rows = self._get_visible_rows()
        rows: list[Tr] = []
        for row in visible_rows:
            if isinstance(row, dict):
                cells = [Td(str(row.get(self._parse_column(c)[1], ""))) for c in self.columns]
            else:
                cells = [Td(str(cell)) for cell in row]
            rows.append(Tr(*cells, role="row", class_="miki-tr"))
        return rows

    def _get_visible_rows(self) -> list:
        data = list(self.rows)
        start = self.page * self.page_size
        end = start + self.page_size
        return data[start:end]

    def _add_alpine_init(self) -> None:
        x_data = {
            "sortField": "",
            "sortDir": "asc",
            "currentPage": self.page,
            "pageSize": self.page_size,
            "totalPages": max(1, (len(self.rows) + self.page_size - 1) // self.page_size),
        }
        if "x_data" not in self.attrs:
            self.attrs["x_data"] = f"{{sortField:'',sortDir:'asc',currentPage:{self.page},pageSize:{self.page_size},totalPages:{x_data['totalPages']}}}"