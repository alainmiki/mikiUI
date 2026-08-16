"""HTML page rendering and the MikiUI base template.

Route handlers return component trees. `render_page` wraps a tree in a full
document (used on navigation / route change), while `render_fragment` is used
for HTMX partial updates that swap a fragment in place.

## Theme Integration

The renderer supports three layers of theming:

1. **Framework CSS** (optional): Loaded via `<link>` from CDN or local path.
   Enables Tailwind or Bootstrap. The framework may also include JS (Bootstrap bundle).

2. **Base MikiUI CSS** (`miki.css`): Always loads. Uses CSS custom properties
   (`--miki-*`) for colors, spacing, radius, etc. This allows themes to change
   appearance by only updating variables.

3. **Color Theme CSS**: Inlined at render time. Sets the `--miki-*` variables
   for light/dark/dracula/etc. Theme plugins may also provide custom CSS.

For Tailwind JIT builds, run:
```
mikiui build --target web --mode fullstack --theme tailwind
```
This scans your app's components/widgets and generates `dist/mikiui.css`.
"""

from __future__ import annotations

import html as _html
import os
from collections.abc import Iterable
from typing import Any

from .dom import Element, I18nText, Text, normalize, render


def _esc(value: Any) -> str:
    """Escape a value for safe insertion into HTML."""
    return _html.escape(str(value), quote=True)


BASE_TEMPLATE = """<!doctype html>
<html lang="{html_lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{page_title}</title>
  {favicon}
  {theme_links}
  {base_css}
  {theme_inline_css}
  {theme_vars}
  {head_extra}
  {runtime_scripts}
  {js_tags}
</head>
<body data-miki-theme="{active_theme}"{body_class_attr}>
{body}
</body>
</html>
"""


def _style_tag(href: str, media: str = "all", rel: str = "stylesheet") -> str:
    return f'  <link rel="{_esc(rel)}" href="{_esc(href)}" media="{_esc(media)}" />'


def _script_tag(src: str, defer: bool = True, type_: str | None = None) -> str:
    parts = []
    if type_:
        parts.append(f'type="{_esc(type_)}"')
    if defer:
        parts.append("defer")
    attrs = " ".join(parts)
    return f'  <script src="{_esc(src)}" {attrs}></script>'


def _theme_styles(theme_name: str) -> dict[str, Any]:
    """Build theme injection data.

    Returns a dict with:
    - links: CSS <link> tags (framework CSS, CDN or local)
    - inline_css: <style> blocks (color theme + user CSS)
    - body_attrs: additional body attributes (classes/data attributes)
    - variables: CSS :root style block with --miki-* variables
    """
    from ..themes import _RUNTIME_DIR, get_theme

    theme = get_theme(theme_name)
    result: dict[str, Any] = {
        "links": [],
        "inline_css": [],
        "body_attrs": "",
        "variables": "",
        "js_tags": "",
    }

    if theme is None:
        return result

    # Framework CSS links (Tailwind, Bootstrap, or custom CSS file)
    if theme.framework == "tailwind":
        if theme.cdn_url:
            result["links"].append(_style_tag(theme.cdn_url))
        elif theme.css_path:
            href = theme.css_path
            if os.path.isabs(theme.css_path):
                rel_path = os.path.relpath(theme.css_path, os.path.join(_RUNTIME_DIR, "themes"))
                href = f"/_miki/runtime/themes/{rel_path}"
            if theme.css_path.startswith("http"):
                href = theme.css_path
            result["links"].append(_style_tag(href))
    elif theme.framework == "bootstrap":
        if theme.cdn_url:
            result["links"].append(_style_tag(theme.cdn_url))
        if theme.js_url:
            result["js_tags"] = _script_tag(theme.js_url)
        if theme.css_path:
            href = theme.css_path
            if os.path.isabs(theme.css_path):
                rel_path = os.path.relpath(theme.css_path, os.path.join(_RUNTIME_DIR, "themes"))
                href = f"/_miki/runtime/themes/{rel_path}"
            if theme.css_path.startswith("http"):
                href = theme.css_path
            result["links"].append(_style_tag(href))
    elif theme.framework is None or theme.framework == "css":
        if theme.css_path:
            href = theme.css_path
            if os.path.isabs(theme.css_path):
                rel_path = os.path.relpath(theme.css_path, os.path.join(_RUNTIME_DIR, "themes"))
                href = f"/_miki/runtime/themes/{rel_path}"
            if theme.css_path.startswith("http"):
                href = theme.css_path
            result["links"].append(_style_tag(href))
    else:
        if theme.cdn_url:
            result["links"].append(_style_tag(theme.cdn_url))

    # Color theme inline CSS (merges with base miki.css)
    color_css = theme.css()
    if color_css:
        result["inline_css"].append(f"<style id=\"miki-theme\">{color_css}</style>")

    # Body classes/data attributes
    extra = list(theme.extra_classes) or []
    data_attrs = ""
    if theme.framework == "tailwind" and "daisyui" in (theme.source or "").lower():
        data_attrs = f" data-theme=\"mikiui-{_esc(theme_name)}\""
    if extra:
        result["body_attrs"] = f" class=\"{ _esc(' '.join(extra)) }\"{data_attrs}"
    elif data_attrs:
        result["body_attrs"] = data_attrs

    # CSS variables layer (overrides theme settings)
    if theme.variables:
        vars_css = ":root { " + "; ".join(f"{_esc(k)}: {_esc(v)}" for k, v in theme.variables.items()) + " }"
        result["variables"] = f"<style>{vars_css}</style>"

    return result


def _script_tags(scripts: Iterable[str]) -> str:
    tags = []
    for src in scripts:
        if src.startswith("http") or src.endswith(".js"):
            tags.append(_script_tag(src))
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
    theme: str = "light",
    framework: str | None = None,
    favicon: str | None = None,
    icon: str | None = None,
) -> str:
    """Wrap a component tree in a full HTML document.

    Parameters
    ----------
    tree
        The component tree (Element, list, string, etc.).
    title, lang
        Page metadata.
    head_extra
        Additional HTML to inject in ``<head>`` (e.g., additional meta tags).
    runtime_scripts
        Iterable of JS script URLs or inline script content. If ``None``, uses the
        default runtime (HTMX + Alpine) from the local bundled files.
    theme
        Theme name (e.g. "light", "dark", "tailwind"). Use ``app.set_theme()``
        at runtime or set ``app.theme`` before render.
    favicon
        Path to favicon.ico or PNG (relative to app root or CDN URL).
    icon
        Desktop window icon (for pywebview; path to .ico/.png file).
    framework
        Optional override for the framework CSS. If ``None``, uses the theme's
        configured framework. Set to "tailwind" or "bootstrap" to force a framework.

    Returns
    -------
    str
        A complete HTML document.
    """
    body = render(tree)
    if runtime_scripts is None:
        from ..runtime.runtime_loader import runtime_scripts as _rs

        runtime_scripts = _rs("local")

    # Build favicon tag
    favicon_tag = ""
    if favicon:
        favicon_tag = f"  <link rel=\"icon\" href=\"{_esc(favicon)}\" type=\"image/png\" />"

    # Resolve framework override or use theme's framework
    theme_data = _theme_styles(theme)

    # Build the HEAD content
    links = "\n".join(theme_data.get("links", []))
    base_css = _style_tag("/_miki/runtime/miki.css")
    inline = "\n".join(theme_data.get("inline_css", []))
    vars_css = theme_data.get("variables", "")
    js_tags = "\n".join(theme_data.get("js_tags", []))

    scripts = _script_tags(runtime_scripts)

    return BASE_TEMPLATE.format(
        html_lang=_esc(lang),
        page_title=_esc(title),
        favicon=favicon_tag,
        theme_links=links,
        base_css=base_css,
        theme_inline_css=inline,
        theme_vars=vars_css,
        body_class_attr=theme_data.get("body_attrs", ""),
        head_extra=head_extra,
        runtime_scripts=scripts,
        js_tags=js_tags,
        active_theme=_esc(theme),
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
    "BASE_TEMPLATE",
]