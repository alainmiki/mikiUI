"""Python<->JS communication bridge for MikiUI.

This module provides the Python-side utilities that generate safe, validated
event bindings and data attributes. All interactivity flows through a single
centralized JS dispatcher (``mikiBridge`` in ``runtime/js/miki_bridge.js``)
so that:

* Widget functions are looked up safely at runtime (no ReferenceErrors when a
  module hasn't loaded).
* All event types -- DOM events, CustomEvents, HTMX swaps, SSE, WebSocket --
  are routed through one consistent API.
* Components emit ``data-miki-on`` attributes that the bridge's auto-init
  layer picks up, so behaviour works even on dynamically injected content
  (HTMX partial swaps).

Public API
----------
``bridge_handler``       -- build a JS dispatch string for an inline handler.
``bridge_attr``          -- build a ``data-miki-on`` attribute value.
``bridge_bind``          -- attach a named event to an element via attributes.
``BridgeEvent``          -- declarative event-binding builder.
``format_detail``        -- JSON-serialize an event detail payload safely.
"""

from __future__ import annotations

import json
import re
import uuid
from typing import Any

__all__ = [
    "bridge_handler",
    "bridge_attr",
    "bridge_bind",
    "BridgeEvent",
    "format_detail",
    "generate_bridge_id",
]

_DOTTED_PATH = re.compile(r"^([a-zA-Z_$][\w$]*)\.([a-zA-Z_$][\w$]*)$")


def generate_bridge_id(prefix: str = "miki") -> str:
    """Generate a unique ID for a bridge target element."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def format_detail(detail: Any) -> str:
    """JSON-serialize an event *detail* payload as a JS object literal.

    Returns a string like ``{group: "abc", index: 0}`` that can be embedded
    inside a ``data-miki-on`` value or an inline ``onclick`` handler.
    """
    if detail is None:
        return "{}"
    return json.dumps(detail, ensure_ascii=False)


def _js_str(value: str) -> str:
    """Return a JS string literal (JSON-quoted, escaped)."""
    return json.dumps(str(value), ensure_ascii=False)


def _js_value(value: Any) -> str:
    """Serialize a Python value to a JS literal expression."""
    if isinstance(value, str):
        return _js_str(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False)


def _format_target(target: Any) -> str:
    """Format a target argument for the JS dispatch call."""
    if isinstance(target, str):
        if target in ("this", "self"):
            return target
        return _js_str(target)
    return str(target)


def _is_dotted_path(action: str) -> tuple[str, str] | None:
    """If *action* is a ``module.method`` path, return (module, method)."""
    m = _DOTTED_PATH.match(action.strip())
    if m:
        return m.group(1), m.group(2)
    return None


def _safe_action(action: str, detail: Any = None) -> str:
    """Wrap *action* so missing modules do not throw ReferenceErrors.

    For dotted paths ``"mikiTabs.show"`` the detail dict values are passed
    as positional arguments via ``mikiBridge.call``.

    For arbitrary JS expressions (e.g. ``"mikiDialog.close(this.closest('dialog'))"``)
    the expression is returned as-is -- the JS bridge evaluates it in a
    try/catch via ``mikiBridge.callSafe``.
    """
    parsed = _is_dotted_path(action)
    if parsed:
        module_name, fn_name = parsed
        if isinstance(detail, dict) and detail:
            args_str = ", ".join(_js_value(v) for v in detail.values())
            return f"mikiBridge.call({_js_str(module_name)},{_js_str(fn_name)},{args_str})"
        return f"mikiBridge.call({_js_str(module_name)},{_js_str(fn_name)})"
    return action


def bridge_handler(
    event_name: str,
    action: str,
    detail: Any = None,
    *,
    target: Any = None,
) -> str:
    """Build a JS dispatch string for an inline event handler.

    Parameters
    ----------
    event_name:
        The logical event name (e.g. ``"select-tab"``, ``"close"``).
    action:
        Either a dotted-path widget function (``"mikiTabs.show"``) that is
        called safely via ``mikiBridge.call``, or an arbitrary JS expression.
    detail:
        Optional payload. For dotted-path actions, dict values are passed as
        positional args to the function *and* as the event detail.
    target:
        Target selector or ``"this"`` (default).

    Returns
    -------
    str
        A JS expression string, e.g.::
            mikiBridge.dispatch(this,"select-tab",mikiBridge.callSafe(function(){mikiBridge.call("mikiTabs","show","grp",0)},this),{group:"grp",index:0})
    """
    tgt = "this" if target is None else _format_target(target)
    detail_str = format_detail(detail)
    safe_action = _safe_action(action, detail)
    return (
        f"mikiBridge.dispatch({tgt},{_js_str(event_name)},"
        f"mikiBridge.callSafe(function(){{{safe_action}}},this),{detail_str})"
    )


def bridge_attr(
    event_name: str,
    action: str,
    detail: Any = None,
    **extra: Any,
) -> dict[str, Any]:
    """Return a dict of attributes suitable for element construction.

    The primary attribute is ``data-miki-on`` whose value encodes one or more
    event bindings separated by ``~|``. Extra kwargs become additional
    ``data-`` attributes on the element so the JS side can read configuration.
    """
    handler = bridge_handler(event_name, action, detail)
    attrs: dict[str, Any] = {"data-miki-on": f"{event_name}::{handler}"}
    for key, val in extra.items():
        attr_name = key.replace("__", "-") if "__" in key else key.replace("_", "-")
        attrs[attr_name] = str(val)
    return attrs


def bridge_bind(
    element_attrs: dict[str, Any],
    event_name: str,
    action: str,
    detail: Any = None,
    **extra: Any,
) -> dict[str, Any]:
    """Merge a bridge event binding into an existing attrs dict.

    ``element_attrs`` is mutated and returned for chaining.
    """
    bridge_attrs = bridge_attr(event_name, action, detail, **extra)
    for key, val in bridge_attrs.items():
        element_attrs[key] = val
    return element_attrs


class BridgeEvent:
    """Declarative builder for a single bridge-bound event.

    Usage::

        ev = BridgeEvent("click", "mikiTabs.show", {"group": "mygroup", "index": 0})
        ev.apply_to(attrs)
    """

    def __init__(
        self,
        event_name: str,
        action: str,
        detail: Any = None,
        **extra: Any,
    ) -> None:
        self.event_name = event_name
        self.action = action
        self.detail = detail
        self.extra = extra

    def to_attrs(self) -> dict[str, Any]:
        """Return a dict of attributes representing this event binding."""
        return bridge_attr(self.event_name, self.action, self.detail, **self.extra)

    def apply_to(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Merge this event binding into *attrs* (mutating it)."""
        return bridge_bind(attrs, self.event_name, self.action, self.detail, **self.extra)

    def __call__(self, attrs: dict[str, Any]) -> dict[str, Any]:
        return self.apply_to(attrs)

    def __repr__(self) -> str:
        return f"BridgeEvent({self.event_name!r}, {self.action!r}, detail={self.detail!r})"
