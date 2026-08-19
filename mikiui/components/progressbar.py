"""Progress and meter components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Progress(Component):
    """A styled ``<progress>`` element with JS-driven value updates.

    ``value`` and ``max`` map to the native attributes.  ``variant`` can be
    ``"default"`` (filled bar) or ``"striped"`` (diagonal stripes animation).

    ``miki_ui.js`` auto-initializes progress elements with
    ``data-miki-progress="true"``.
    """

    tag = "progress"

    def __init__(self, *children: Any, value: float = 0, max: float = 100, variant: str = "default", **attrs: Any    ) -> None:
        self.value = value
        self.max = max
        classes = "miki-progress"
        if variant == "striped":
            classes += " miki-progress-striped"
        user_classes = attrs.pop("class_", "")
        attrs["class_"] = f"{classes} {user_classes}".strip()
        attrs.setdefault("value", value)
        attrs.setdefault("max", max)
        attrs.setdefault("data-miki-progress", "true")
        attrs.setdefault("data-value", str(value))
        attrs.setdefault("data-max", str(max))
        attrs.setdefault("aria-valuenow", str(value))
        attrs.setdefault("aria-valuemin", "0")
        attrs.setdefault("aria-valuemax", str(max))
        super().__init__(*children, **attrs)

    def to_html(self) -> str:
        # <progress> children go before the closing tag
        return super().to_html()


class Meter(Component):
    """A styled ``<meter>`` element.

    ``value``, ``min``, ``max``, ``low``, ``high``, ``optimum`` map to native
    attributes.  ``variant`` can be ``"default"`` or ``"colored"``.
    """

    tag = "meter"

    def __init__(self, *children: Any, value: float = 0, min: float = 0, max: float = 1, **attrs: Any) -> None:
        classes = "miki-meter"
        user_classes = attrs.pop("class_", "")
        attrs["class_"] = f"{classes} {user_classes}".strip()
        attrs.setdefault("value", value)
        attrs.setdefault("min", min)
        attrs.setdefault("max", max)
        super().__init__(*children, **attrs)


class Output(Component):
    """A styled ``<output>`` element."""

    tag = "output"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-output")
        super().__init__(*children, **attrs)


ProgressBar = Progress
