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

import json
from typing import Any

from ..components import Button, Div, Input, Option, Select, Span, Table, Tbody, Td, Th, Thead, Tr
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
        sort_by: str | None = None,
        sort_order: str = "asc",
        filter_by: dict[str, str] | None = None,
        search_query: str | None = None,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-datagrid")
        attrs.setdefault("role", "grid")
        attrs.setdefault("aria_label", "Data grid")
        attrs.setdefault("data-miki-datagrid", "true")
        attrs.setdefault("touch-action", "manipulation")
        attrs.setdefault("tabindex", "0")

        if htmx_get:
            attrs.setdefault("data-miki-htmx-get", htmx_get)
        if htmx_target:
            attrs.setdefault("data-miki-htmx-target", htmx_target)
        if pagination:
            attrs.setdefault("data-miki-page-size", str(page_size))

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
        self.sort_by = sort_by
        self.sort_order = sort_order if sort_order in ("asc", "desc") else "asc"
        self.filter_by = filter_by or {}
        self.search_query = search_query or ""

        if not htmx_get and rows:
            normalized = [self._normalize_row(r) for r in rows]
            try:
                rows_json = json.dumps(normalized)
                attrs.setdefault("data-miki-rows", rows_json)
            except (TypeError, ValueError):
                pass

        children: list[Any] = []

        if search:
            search_children: list[Any] = []
            if search_fields:
                options: list[Any] = []
                for f in search_fields:
                    options.append(Option(f, value=f))
                select = Select(*options, name="search_field", class_="miki-search-field-select")
                search_children.append(select)
            search_input = Input(type="search", placeholder=_("search_placeholder", "Search..."), **{"data-miki-search": "true"})
            search_children.append(search_input)
            search_div = Div(*search_children, class_="miki-datagrid-search")
            children.append(search_div)

        thead_children = self._build_column_headers()
        thead = Thead(*thead_children, class_="miki-datagrid-head")
        tbody_children = self._build_body_rows()
        tbody = Tbody(*tbody_children)

        table_attrs: dict[str, Any] = {}
        if height:
            table_attrs["class_"] = "miki-datagrid-scrollable"
            table_attrs.setdefault("style", f"max-height: {height}px;")

        table = Table(thead, tbody, **table_attrs)
        children.append(table)

        if pagination:
            filtered_count = len(self._get_filtered_sorted_rows())
            total_pages = max(1, (filtered_count + self.page_size - 1) // self.page_size)
            prev_btn = Button(_("pagination_prev", "Previous"), **{"data-miki-page": "prev"})
            page_info = Span(
                f"{_('pagination_page', 'Page')} {page + 1} {_('pagination_of', 'of')} {total_pages}",
                **{"data-miki-page-info": "true"},
            )
            next_btn = Button(_("pagination_next", "Next"), **{"data-miki-page": "next"})
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

    def _parse_columns(self) -> tuple[list[str], list[str], list[dict]]:
        labels: list[str] = []
        fields: list[str] = []
        options: list[dict] = []
        for col in self.columns:
            label, field, opts = self._parse_column(col)
            labels.append(label)
            fields.append(field)
            options.append(opts)
        return labels, fields, options

    def _normalize_row(self, row: dict | list) -> dict:
        if isinstance(row, dict):
            return dict(row)
        _, fields, _ = self._parse_columns()
        return {
            fields[i] if i < len(fields) else str(i): row[i] if i < len(row) else ""
            for i in range(max(len(fields), len(row)))
        }

    def _apply_search(self, data: list) -> list:
        if not self.search_query:
            return data
        q = self.search_query.lower()
        if not data:
            return data
        if self.search_fields:
            return [
                r for r in data
                if isinstance(r, dict) and any(
                    q in str(r.get(f, "")).lower() for f in self.search_fields
                )
            ]
        if isinstance(data[0], dict):
            return [r for r in data if any(q in str(v).lower() for v in r.values())]
        return [r for r in data if any(q in str(c).lower() for c in r)]

    def _apply_filter(self, data: list) -> list:
        if not self.filter_by:
            return data
        result: list = []
        for row in data:
            if not isinstance(row, dict):
                continue
            match = True
            for field, value in self.filter_by.items():
                if value and value.lower() not in str(row.get(field, "")).lower():
                    match = False
                    break
            if match:
                result.append(row)
        return result

    def _apply_sort(self, data: list) -> list:
        if not self.sort_by:
            return data
        reverse = self.sort_order == "desc"

        def sort_key(row: dict) -> tuple[int, float | str]:
            val = row.get(self.sort_by, "")
            try:
                return (0, float(val))
            except (ValueError, TypeError):
                return (1, str(val).lower())

        try:
            return sorted(data, key=sort_key, reverse=reverse)
        except (TypeError, ValueError):
            return data

    def _get_filtered_sorted_rows(self) -> list:
        data = list(self.rows)
        data = self._apply_search(data)
        data = self._apply_filter(data)
        data = self._apply_sort(data)
        return data

    def _build_column_headers(self) -> list[Th]:
        headers: list[Th] = []
        for col in self.columns:
            label, field, opts = self._parse_column(col)
            th_classes = ["miki-th"]
            if opts.get("width"):
                th_classes.append(f"miki-th-width-{opts['width']}")
            if opts.get("align"):
                th_classes.append(f"miki-th-{opts['align']}")

            th_attrs: dict[str, Any] = {
                "class_": " ".join(th_classes),
                "data-miki-col-field": field,
            }
            if opts.get("type") == "number":
                th_attrs["class_"] += " miki-th-number"
            if opts.get("align"):
                th_attrs["class_"] += f" miki-text-{opts['align']}"

            if not opts.get("sortable", False):
                if opts.get("filterable", False):
                    th_attrs["class_"] += " miki-th-filter"
                    filter_input = Input(
                        type="search", placeholder=_("filter_placeholder", "Filter {col}").format(col=label), **{"data-miki-filter": "true"}
                    )
                    headers.append(Th(label, filter_input, **th_attrs))
                else:
                    headers.append(Th(label, **th_attrs))
            else:
                th_attrs["data-miki-sort-field"] = field
                th_attrs.setdefault("role", "button")
                th_attrs.setdefault("tabindex", "0")
                th_attrs.setdefault("aria-sort", "none")
                th_attrs.setdefault("aria_label", f"Sort by {label}")
                th_attrs["class_"] += " miki-th-sortable"
                sort_indicator = Span("▲", class_="miki-sort-indicator", **{"data-miki-sort-indicator": "true"})
                if opts.get("filterable", False):
                    th_attrs["class_"] += " miki-th-filter"
                    filter_input = Input(
                        type="search", placeholder=_("filter_placeholder", "Filter {col}").format(col=label), **{"data-miki-filter": "true"}
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
        data = self._get_filtered_sorted_rows()
        start = self.page * self.page_size
        end = start + self.page_size
        return data[start:end]
