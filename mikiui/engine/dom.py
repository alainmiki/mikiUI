"""DOM model and HTML serialization for MikiUI.

This module is dependency-free so the renderer can be unit-tested and used
without a running server. It defines the node types that components render to
and the logic that turns them into safe HTML.
"""

from __future__ import annotations

import html
import re
from collections.abc import Mapping
from typing import Any

# HTML void elements: they have no closing tag and no children.
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}

_DANGEROUS_TAGS = re.compile(
    r"</?(?:script|iframe|object|embed|form|input|button|style|link|meta|base|applet|svg|math|img|video|audio|source|track|frame|frameset|noscript)\b[^>]*>",
    re.IGNORECASE,
)
_DANGEROUS_ATTRS = re.compile(
    r'\s(?:on\w+|href|src|action|formaction|background|cite|codebase|data|dynsrc|lowsrc)\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+)',
    re.IGNORECASE,
)


def sanitize_html(value: str, *, allow_tags: list[str] | None = None) -> str:
    """Strip dangerous HTML tags and event-handler attributes from ``value``.

    Parameters
    ----------
    value:
        Raw HTML string.
    allow_tags:
        Optional whitelist of tag names to keep. When ``None``, all tags are
        stripped (text-only output).

    Returns
    -------
    str
        Sanitized HTML.
    """
    if allow_tags is not None:
        allowed = set(t.lower() for t in allow_tags)
        tag_pattern = re.compile(r"</?([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")
        def _filter(m: re.Match[str]) -> str:
            tag = m.group(1).lower()
            return m.group(0) if tag in allowed else ""
        value = tag_pattern.sub(_filter, value)
    else:
        value = _DANGEROUS_TAGS.sub("", value)
    value = _DANGEROUS_ATTRS.sub("", value)
    return value


def escape_attr(value: str) -> str:
    """Escape a value for safe insertion into an HTML attribute."""
    return html.escape(str(value), quote=True)


def truncate(value: str, length: int = 100, suffix: str = "...") -> str:
    """Truncate ``value`` to ``length`` characters and append ``suffix``."""
    text = str(value)
    if len(text) <= length:
        return text
    return text[: length - len(suffix)] + suffix


# --- Internationalization hook ------------------------------------------------
# Components mark translatable text with `_("key", "Default")`. A translator can
# be registered globally; otherwise the default text is used and the key is
# emitted as `data-i18n` so client-side runtimes can re-translate.

_translator = None


def set_translator(fn: Any) -> None:
    """Register a translator callable ``fn(key, default) -> str``."""
    global _translator
    _translator = fn


def get_translator() -> Any:
    return _translator


def _(key: str, default: str | None = None) -> I18nText:
    """Mark ``default`` as translatable under ``key`` (i18n hook)."""
    if default is None:
        default = key
    return I18nText(key, default)


class I18nText:
    """A translatable text node. Rendered with a ``data-i18n`` attribute."""

    __slots__ = ("key", "default")

    def __init__(self, key: str, default: str) -> None:
        self.key = key
        self.default = default

    def __str__(self) -> str:
        text = _translator(self.key, self.default) if _translator else self.default
        return str(text)

    def format(self, **kwargs: Any) -> str:
        """Resolve the translation and format it with ``str.format(**kwargs)``."""
        text = _translator(self.key, self.default) if _translator else self.default
        return str(text).format(**kwargs)

    def __repr__(self) -> str:
        return f"I18nText(key={self.key!r}, default={self.default!r})"

    def to_html(self) -> str:
        text = _translator(self.key, self.default) if _translator else self.default
        return (
            f'<span data-i18n="{html.escape(self.key, True)}">'
            f"{html.escape(str(text), quote=False)}</span>"
        )


class Text:
    """A plain text node. Always HTML-escaped."""

    __slots__ = ("content",)

    def __init__(self, content: Any) -> None:
        self.content = content

    def to_html(self) -> str:
        return html.escape(str(self.content), quote=False)


class RawHtml:
    """A node containing raw, unescaped HTML.

    Used by components that need to emit trusted HTML (e.g. inline SVG in
    charts). The caller is responsible for ensuring the content is safe.
    """

    __slots__ = ("content",)

    def __init__(self, content: str) -> None:
        self.content = content

    def to_html(self) -> str:
        return str(self.content)


def _render_child(child: Any) -> str:
    if child is None or child is False:
        return ""
    if isinstance(child, (Element, Text, I18nText, RawHtml)):
        return child.to_html()
    if isinstance(child, (list, tuple)):
        return "".join(_render_child(c) for c in child)
    return html.escape(str(child), quote=False)


# SVG attributes that must preserve camelCase (SVG is case-sensitive)
_SVG_CAMELCASE_ATTRS = frozenset({
    "viewBox", "preserveAspectRatio", "gradientTransform", "gradientUnits",
    "patternTransform", "patternUnits", "clipPath", "clipPathUnits",
    "maskContentUnits", "maskUnits", "pathLength", "pointsAtX", "pointsAtY",
    "pointsAtZ", "refX", "refY", "markerHeight", "markerWidth", "markerUnits",
    "textLength", "lengthAdjust", "spreadMethod", "stdDeviation", "baseFrequency",
    "numOctaves", "stitchTiles", "surfaceScale", "specularConstant",
    "specularExponent", "kernelMatrix", "kernelUnitLength", "targetX", "targetY",
    "xChannelSelector", "yChannelSelector", "tableValues", "xHeight", "capHeight",
    "horizAdvX", "horizOriginX", "vertAdvY", "vertOriginY", "unicodeRange",
    "panose1", "bbox", "unitsPerEm", "stemv", "stemh", "slope", "overlinePosition",
    "underlinePosition", "ascent", "descent", "mathline", "topline", "centerline",
    "alphabetic", "ideographic", "hanging", "xmlnsXlink",
})


def _attr_name(key: str) -> str:
    # Python keyword collisions use a trailing underscore (class_, for_).
    if key == "class_":
        return "class"
    if key == "for_":
        return "for"
    # Preserve camelCase for known SVG attributes
    if key in _SVG_CAMELCASE_ATTRS:
        return key
    # Generic mapping: underscores become hyphens so aria_label -> aria-label,
    # data_foo -> data-foo, and hx_get -> hx-get (HTMX attributes).
    return key.replace("_", "-")


class Element:
    """A renderable HTML element with attributes and children."""

    tag: str = "div"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        self.children: list[Any] = list(children)
        self.tag = attrs.pop("tag", self.__class__.tag)
        self.attrs: dict[str, Any] = attrs

    # -- tree manipulation -----------------------------------------------------
    def append(self, *children: Any) -> Element:
        self.children.extend(children)
        return self

    def with_id(self, id: str) -> Element:
        self.attrs["id"] = id
        return self

    # -- serialization ---------------------------------------------------------
    def _render_attrs(self) -> str:
        parts: list[str] = []
        for key, value in self.attrs.items():
            if value is None or value is False:
                continue
            name = _attr_name(key)
            if value is True:
                parts.append(name)
                continue
            if name == "style" and isinstance(value, Mapping):
                value = "; ".join(f"{k}:{v}" for k, v in value.items())
            elif name == "class" and isinstance(value, (list, tuple, set)):
                value = " ".join(str(v) for v in value if v)
            elif isinstance(value, (list, tuple, set)) and name != "class":
                value = " ".join(str(v) for v in value if v)
            parts.append(f'{name}="{escape_attr(str(value))}"')
        return " ".join(parts)

    def to_html(self) -> str:
        attr_str = self._render_attrs()
        open_tag = f"<{self.tag}" + (f" {attr_str}" if attr_str else "") + ">"
        if self.tag in VOID_TAGS:
            # Emit a self-closing style void tag for clarity.
            return open_tag[:-1] + " />"
        inner = "".join(_render_child(c) for c in self.children)
        return f"{open_tag}{inner}</{self.tag}>"

    def __str__(self) -> str:
        return self.to_html()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} tag={self.tag!r} #{len(self.children)} children>"


def render(node: Any) -> str:
    """Render any node (Element/Text/I18nText/RawHtml/str/list) to an HTML string."""
    if node is None or node is False:
        return ""
    if isinstance(node, (Element, Text, I18nText, RawHtml)):
        return node.to_html()
    if isinstance(node, (list, tuple)):
        return "".join(_render_child(c) for c in node)
    return html.escape(str(node), quote=False)


def normalize(node: Any) -> list[Any]:
    """Normalize a route handler return value into a list of renderable nodes."""
    if node is None or node is False:
        return []
    if isinstance(node, (Element, Text, I18nText, RawHtml)):
        return [node]
    if isinstance(node, (list, tuple)):
        out: list[Any] = []
        for child in node:
            out.extend(normalize(child))
        return out
    return [Text(node)]
