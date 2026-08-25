"""MikiUI rendering engine.

Provides the DOM model, HTML serialization, i18n hook, the page/fragment
renderer, and the Python<->JS communication bridge used by the backend and CLI.
"""

from __future__ import annotations

from .bridge import (
    BridgeEvent,
    bridge_attr,
    bridge_bind,
    bridge_handler,
    format_detail,
    generate_bridge_id,
)
from .dom import (
    Element,
    I18nText,
    RawHtml,
    Text,
    _,
    get_translator,
    normalize,
    render,
    set_translator,
)
from .renderer import render_fragment, render_page

__all__ = [
    "Element",
    "Text",
    "I18nText",
    "RawHtml",
    "_",
    "render",
    "normalize",
    "set_translator",
    "get_translator",
    "render_page",
    "render_fragment",
    "BridgeEvent",
    "bridge_attr",
    "bridge_bind",
    "bridge_handler",
    "format_detail",
    "generate_bridge_id",
]
