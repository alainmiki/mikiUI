"""HTML page rendering and the MikiUI base template.

Route handlers return component trees. `render_page` wraps a tree in a full
document (used on navigation / route change), while `render` is used for HTMX
partial updates that swap a fragment in place.
"""

from __future__ import annotations

from typing import Any, Iterable

from .dom import Element, I18nText, Text, normalize, render


BASE_TEMPLATE = """<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="/_miki/runtime/miki.css" />
  {head_extra}
  {runtime_scripts}
</head>
<body>
{body}
</body>
</html>
"""


def _script_tags(scripts: Iterable[str]) -> str:
    tags = []
    for src in scripts:
        if src.startswith("http") or src.endswith(".js"):
            tags.append(f'  <script src="{src}" defer></script>')
        else:
            tags.append(f"  {src}")
    return "\n".join(tags)


def render_page(
    tree: Any,
    *,
    title: str = "MikiUI App",
    lang: str = "en",
    head_extra: str = "",
    runtime_scripts: Iterable[str] | None = None,
) -> str:
    """Wrap a component tree in a full HTML document."""
    body = render(tree)
    if runtime_scripts is None:
        from ..runtime.runtime_loader import runtime_scripts as _rs

        runtime_scripts = _rs("local")
    scripts = _script_tags(runtime_scripts)
    return BASE_TEMPLATE.format(
        lang=lang,
        title=title,
        head_extra=head_extra,
        runtime_scripts=scripts,
        body=body,
    )


def render_fragment(tree: Any) -> str:
    """Render just the component tree (no document wrapper) for partial swaps."""
    return render(tree)


__all__ = [
    "render_page",
    "render_fragment",
    "Element",
    "Text",
    "I18nText",
    "normalize",
    "render",
]
