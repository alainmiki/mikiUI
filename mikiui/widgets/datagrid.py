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
    Enable global search input.
search_fields : list[str] | None
    Field names to include in the search-field dropdown. When provided,
    a ``<select>`` appears before the search box so users can limit the
    search scope to specific columns.
page : int
    Current page (0-indexed)
page_size : int
    Rows per page
height : int | None
    Fixed height in pixels for scrollable container.
htmx_get : str | None
    URL for HTMX-based pagination. When set, page navigation triggers
    an AJAX GET instead of dispatching a custom event.
htmx_target : str | None
    CSS selector for the HTMX response target element.
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

from ..components import Button, Div, Input, Option, Select, Span, Table, Tbody, Td, Th, Thead, Tr
from ..components.base import Component


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

    tag = "div"

    def __init__(
        self,
        columns: list[str | tuple],
        rows: list[dict | list],
        *,
        sortable: bool = True,
        filterable: bool = False,
        pagination: bool = True,
        search: bool = True,
        search_fields: list[str] | None = None,
        page: int = 0,
        page_size: int = 10,
        height: int | None = None,
        htmx_get: str | None = None,
        htmx_target: str | None = None,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class", "miki-datagrid")
        attrs.setdefault("role", "grid")
        attrs.setdefault("data-miki-datagrid", "true")

        if htmx_get:
            attrs.setdefault("data-miki-htmx-get", htmx_get)
        if htmx_target:
            attrs.setdefault("data-miki-htmx-target", htmx_target)

        self.columns = columns
        self.rows = rows
        self.sortable = sortable
        self.filterable = filterable
        self.pagination = pagination
        self.search = search
        self.search_fields = search_fields
        self.page = page
        self.page_size = page_size
        self.height = height

        children: list[Any] = []

        if search:
            search_children: list[Any] = []
            if search_fields:
                options: list[Any] = []
                for f in search_fields:
                    options.append(Option(f, value=f))
                select = Select(*options, name="search_field", class_="miki-search-field-select")
                search_children.append(select)
            search_input = Input(type="search", placeholder="Search...", **{"data-miki-search": "true"})
            search_children.append(search_input)
            search_div = Div(*search_children, class_="miki-datagrid-search")
            children.append(search_div)

        thead_children = self._build_column_headers()
        thead = Thead(*thead_children, class_="miki-datagrid-head")
        tbody_children = self._build_body_rows()
        tbody = Tbody(*tbody_children)

        table_attrs: dict[str, Any] = {}
        if height:
            table_attrs["class"] = "miki-datagrid-scrollable"
            table_attrs.setdefault("style", f"max-height: {height}px;")

        table = Table(thead, tbody, **table_attrs)
        children.append(table)

        if pagination:
            total_pages = max(1, (len(self.rows) + self.page_size - 1) // self.page_size)
            prev_btn = Button("Previous", **{"data-miki-page": "prev"})
            page_info = Span(f"Page {page + 1} of {total_pages}", **{"data-miki-page-info": "true"})
            next_btn = Button("Next", **{"data-miki-page": "next"})
            pagination_div = Div(
                prev_btn, page_info, next_btn, class_="miki-datagrid-pagination", **{"data-miki-pagination": "true"}
            )
            children.append(pagination_div)

        super().__init__(*children, **attrs)

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

            th_attrs: dict[str, Any] = {"class_": " ".join(th_classes)}
            if opts.get("type") == "number":
                th_attrs["class_"] += " miki-th-number"
            if opts.get("align"):
                th_attrs["class_"] += f" miki-text-{opts['align']}"

            if not opts.get("sortable", False):
                if opts.get("filterable", False):
                    th_attrs["class_"] += " miki-th-filter"
                    filter_input = Input(
                        type="search", placeholder=f"Filter {label}...", **{"data-miki-filter": "true"}
                    )
                    headers.append(Th(label, filter_input, **th_attrs))
                else:
                    headers.append(Th(label, **th_attrs))
            else:
                th_attrs["data-miki-sort-field"] = field
                th_attrs.setdefault("role", "button")
                th_attrs.setdefault("tabindex", "0")
                th_attrs.setdefault("aria-sort", "none")
                th_attrs["class_"] += " miki-th-sortable"
                sort_indicator = Span("▲", class_="miki-sort-indicator", **{"data-miki-sort-indicator": "true"})
                if opts.get("filterable", False):
                    th_attrs["class_"] += " miki-th-filter"
                    filter_input = Input(
                        type="search", placeholder=f"Filter {label}...", **{"data-miki-filter": "true"}
                    )
                    headers.append(Th(label, sort_indicator, filter_input, **th_attrs))
                else:
                    headers.append(Th(label, sort_indicator, **th_attrs))
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
