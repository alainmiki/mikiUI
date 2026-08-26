"""HTML page rendering and the MikiUI base template.

Route handlers return component trees. `render_page` wraps a tree in a full
document (used on navigation / route change), while `render_fragment` is used
for HTMX partial updates that swap a fragment in place.

## Theme Integration

The renderer supports three layers of theming:

1. **Framework CSS** (optional): Loaded via `<link>` from CDN or local path.
   Enables Tailwind.

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
  {base_css}
  {theme_links}
  {theme_inline_css}
  {theme_vars}
  {head_extra}
  {runtime_scripts}
  {js_tags}
</head>
<body {theme_attr}{body_class_attr}>
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


def _theme_styles(
    theme_name: str,
    framework: str | None = None,
    style_mode: str = "cdn",
    daisyui: bool = False,
    csp_nonce: str | None = None,
) -> dict[str, Any]:
    """Build theme injection data.

    Parameters
    ----------
    theme_name:
        The color/framework theme name.
    framework:
        Optional explicit framework override (``"plain"``, ``"tailwind"``).
        When ``None``, the theme's own ``framework`` field is used.
    style_mode:
        Tailwind only. ``"cdn"`` uses public CDN URLs; ``"local"`` serves
        files from ``_miki/runtime/themes/``.
    daisyui:
        Tailwind only. Whether DaisyUI is enabled.

    Returns a dict with:
    - links: CSS <link> tags (framework CSS, color theme CSS, CDN or local)
    - body_attrs: additional body attributes (classes/data attributes)
    - variables: CSS :root style block with --miki-* variable overrides
    """
    from ..themes import get_theme

    theme = get_theme(theme_name)
    result: dict[str, Any] = {
        "links": [],
        "body_attrs": "",
        "variables": "",
        "js_tags": "",
        "theme_obj": theme,
    }

    if theme is None:
        return result

    effective_fw = framework or getattr(theme, "framework", None)

    # Build the URL for the theme CSS file.
    def _theme_href(css_path: str | None) -> str | None:
        if not css_path:
            return None
        if css_path.startswith("http"):
            return css_path
        if os.path.isabs(css_path):
            filename = os.path.basename(css_path)
            return f"/_miki/runtime/themes/{_esc(filename)}"
        return css_path

    # Color theme CSS is served as a static file via /_miki/runtime/themes/<name>.css
    # miki.css is always loaded for component styles; theme CSS files only
    # override :root variables for color themes.
    theme_css_url = None
    if effective_fw == "tailwind":
        pass
    elif theme.css_path and os.path.isfile(theme.css_path):
        theme_css_url = _theme_href(theme.css_path)
    elif theme.framework is None or theme.framework == "css" or effective_fw == "plain":
        theme_css_url = f"/_miki/runtime/themes/{_esc(theme_name)}.css"

    if theme_css_url:
        result["links"].append(_style_tag(theme_css_url))

    # Framework CSS links (Tailwind)
    # miki.css is always loaded for component styles, so we only load the
    # Tailwind CDN for utility classes when using the tailwind framework.
    if effective_fw == "tailwind":
        if style_mode == "local":
            if daisyui:
                result["links"].append(
                    '<link rel="stylesheet" '
                    'href="https://cdn.jsdelivr.net/npm/daisyui@5/dist/daisyui.min.css" '
                    'media="all" />'
                )
        else:
            cdn_url = "https://cdn.jsdelivr.net/npm/tailwindcss@4/dist/tailwind.min.css"
            result["links"].append(_style_tag(cdn_url))
            if daisyui:
                daisyui_cdn = "https://cdn.jsdelivr.net/npm/daisyui@5/dist/daisyui.min.css"
                result["links"].append(_style_tag(daisyui_cdn))

    # Body classes/data attributes
    extra = list(theme.extra_classes) or []
    data_attrs = ""
    if effective_fw == "tailwind":
        color_name = getattr(theme, "color_theme", None) or theme_name
        data_attrs = f" data-theme=\"mikiui-{_esc(color_name)}\""
    if extra:
        result["body_attrs"] = f" class=\"{ _esc(' '.join(extra)) }\"{data_attrs}"
    elif data_attrs:
        result["body_attrs"] = data_attrs

    # CSS variables layer (overrides theme settings)
    if theme.variables:
        vars_css = ":root { " + "; ".join(f"{_esc(k)}: {_esc(v)}" for k, v in theme.variables.items()) + " }"
        nonce_attr = f' nonce="{_esc(csp_nonce)}"' if csp_nonce else ""
        result["variables"] = f"<style{nonce_attr}>{vars_css}</style>"

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
    style_mode: str = "cdn",
    daisyui: bool = False,
    favicon: str | None = None,
    icon: str | None = None,
    csp_nonce: str | None = None,
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
        Color theme name (e.g. "light", "dark", "dracula"). Use ``app.set_theme()``
        at runtime or set ``app.theme`` before render.
    framework
        Styling framework override. One of ``"plain"``, ``"tailwind"``, or ``None``.
        If ``None``, falls back to the theme's configured framework, and for
        backward compatibility ``"tailwind"`` theme name implies Tailwind.
    style_mode
        Tailwind only. ``"cdn"`` uses public CDN; ``"local"`` serves a locally
        built CSS file from ``_miki/runtime/themes/``.
    daisyui
        Tailwind only. Whether to include DaisyUI CSS.
    favicon
        Path to favicon.ico or PNG (relative to app root or CDN URL).
    icon
        Desktop window icon (for pywebview; path to .ico/.png file).

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

    # Resolve framework from explicit parameter or theme registry.
    theme_data = _theme_styles(
        theme,
        framework=framework,
        style_mode=style_mode,
        daisyui=daisyui,
        csp_nonce=csp_nonce,
    )
    active_theme_obj = theme_data.get("theme_obj")

    effective_framework = framework
    if effective_framework is None and active_theme_obj:
        effective_framework = getattr(active_theme_obj, "framework", None)

    # Determine which base CSS to load:
    # - Always load miki.css for component styles and base variables.
    # - Theme CSS files (light.css, tailwind.css, etc.) only set --miki-*
    #   custom properties on :root and provide minimal theme-specific vars.
    base_css = _style_tag("/_miki/runtime/miki.css")
    theme_attr = f'data-miki-theme="{_esc(theme)}"'

    # Build the HEAD content
    links = "\n".join(theme_data.get("links", []))
    inline = "\n".join(theme_data.get("inline_css", []))
    vars_css = theme_data.get("variables", "")
    js_tags = "\n".join(theme_data.get("js_tags", []))

    scripts = _script_tags(runtime_scripts)

    return BASE_TEMPLATE.format(
        html_lang=_esc(lang),
        page_title=_esc(title),
        favicon=favicon_tag,
        base_css=base_css,
        theme_links=links,
        theme_inline_css=inline,
        theme_vars=vars_css,
        theme_attr=theme_attr,
        body_class_attr=theme_data.get("body_attrs", ""),
        head_extra=head_extra,
        runtime_scripts=scripts,
        js_tags=js_tags,
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