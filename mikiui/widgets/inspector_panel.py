"""InspectorPanel widget: inspects an object's public attributes."""

from __future__ import annotations

from typing import Any

from ..components.base import Component
from .property_grid import PropertyGrid


class InspectorPanel(Component):
    """Render an object's public attributes as a :class:`PropertyGrid`.

    Uses ``vars(obj)``/``obj.__dict__`` when available, falling back to
    ``str(obj)`` otherwise.

    :param obj: any Python object to inspect.
    """

    tag = "div"

    def __init__(self, obj: Any, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-inspector")
        attrs.setdefault("role", "region")
        try:
            items = vars(obj)
            if not isinstance(items, dict):
                items = dict(items)
        except TypeError:
            items = {"value": str(obj)}
        super().__init__(PropertyGrid(items), **attrs)
