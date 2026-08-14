"""MikiUI rendering engine.

Provides the DOM model, HTML serialization, i18n hook, and the page/fragment
renderer used by the backend and CLI.
"""

from __future__ import annotations

from .dom import (
    Element,
    Text,
    I18nText,
    _,
    render,
    normalize,
    set_translator,
    get_translator,
)
from .renderer import render_page, render_fragment

__all__ = [
    "Element",
    "Text",
    "I18nText",
    "_",
    "render",
    "normalize",
    "set_translator",
    "get_translator",
    "render_page",
    "render_fragment",
]
