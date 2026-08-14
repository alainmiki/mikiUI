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
        attrs.setdefault("class", "miki-filepicker")
        input_el = Input(
            type="file",
            name=name,
            **({"multiple": True} if multiple else {}),
            **({"accept": accept} if accept else {}),
        )
        super().__init__(
            Label(label, for_=name),
            input_el,
            Span("", class_="miki-filepicker-name"),
            **attrs,
        )
