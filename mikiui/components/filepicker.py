"""FilePicker component (browser upload/download UI)."""

from __future__ import annotations

from typing import Any

from .base import Component
from .input import Input
from .html import Div, Span
from .form import Label


class FilePicker(Component):
    """A labeled file input.

    ``multiple`` and ``accept`` mirror the native ``<input type=file>``.
    On desktop targets this maps to OS file-system APIs (see build system).

    Pass ``class_`` for additional CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        label: str = "Choose file",
        name: str = "file",
        multiple: bool = False,
        accept: str | None = None,
        **attrs: Any,
    ) -> None:
        user_class = attrs.pop("class_", "")
        attrs["class_"] = f"miki-filepicker {user_class}".strip()
        input_attrs: dict[str, Any] = {"type": "file", "name": name, "class_": "miki-file-input"}
        if multiple:
            input_attrs["multiple"] = True
        if accept:
            input_attrs["accept"] = accept
        input_el = Input(**input_attrs)
        super().__init__(
            Label(label, for_=name, class_="miki-file-label"),
            input_el,
            Span("", class_="miki-filepicker-name"),
            **attrs,
        )
