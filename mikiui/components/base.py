"""Base component class and helpers.

A Component is a thin subclass of :class:`mikiui.engine.dom.Element` that pins a
tag and provides a beginner-friendly constructor. Components map 1:1 to HTML
elements; widgets (in `mikiui.widgets`) compose them.
"""

from __future__ import annotations

from typing import Any

from ..engine.dom import Element


class Component(Element):
    """Base class for all MikiUI components.

    Subclasses set ``tag``. Positional args become child content; keyword args
    become HTML attributes (with i18n/ARIA-friendly underscore mapping).
    """

    tag = "div"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        super().__init__(*children, **attrs)

    @classmethod
    def element(cls, *children: Any, **attrs: Any) -> Component:
        return cls(*children, **attrs)


def component(tag: str, *, void: bool = False):
    """Factory for simple pass-through components (e.g. one-off HTML elements)."""

    class _Generated(Component):
        pass

    _Generated.tag = tag
    _Generated.__name__ = tag.capitalize()
    return _Generated
