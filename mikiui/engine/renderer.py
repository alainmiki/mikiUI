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
  {tailwind_script}
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


def _tailwind_config_script(theme_name: str, daisyui: bool = False, csp_nonce: str | None = None) -> str:
    """Generate Tailwind v4 configuration via inline CSS (type="text/tailwindcss").
    
    Tailwind v4 dropped the ``tailwind.config = {}`` JavaScript API.  Configuration
    now happens inside ``<style type="text/tailwindcss">`` blocks using the
    ``@theme`` directive.  The browser CDN scans the DOM for utility classes
    automatically, so no content paths are required.
    """
    from ..themes import get_theme
    
    theme = get_theme(theme_name)
    theme_vars_lines: list[str] = []
    if theme is not None:
        for k, v in (theme.variables or {}).items():
            if k.startswith("--miki-"):
                tw_key = "--color-" + k[len("--miki-"):].replace("_", "-")
                theme_vars_lines.append(f"  {tw_key}: {_esc(v)};")
    
    daisyui_theme = ""
    if daisyui:
        daisyui_theme = (
            "\n  --color-primary: #3b82f6;\n"
            "  --color-secondary: #60a5fa;\n"
            "  --color-accent: #3b82f6;\n"
            "  --color-neutral: #1e293b;\n"
            "  --color-base-100: #0f172a;\n"
            "  --color-base-200: #1e293b;\n"
            "  --color-base-300: #334155;\n"
        )
    
    nonce_attr = f' nonce="{_esc(csp_nonce)}"' if csp_nonce else ""
    
    all_vars = "\n".join(theme_vars_lines) + daisyui_theme
    if not all_vars.strip():
        return '<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>'
    
    return f'''<script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
<style{nonce_attr} type="text/tailwindcss">
@theme {{
{all_vars}
}}
</style>'''


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
        "js_tags": [],
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

    # Framework CSS must be loaded FIRST for proper cascade.
    # For Tailwind: loads Tailwind CSS (local) or Tailwind JS (CDN).
    # For plain: no framework CSS to load.
    if effective_fw == "tailwind":
        if style_mode == "local":
            result["links"].append(_style_tag("/_miki/runtime/themes/tailwind.css"))
        else:
            # CDN mode: DaisyUI v5 requires Tailwind v4 (@tailwindcss/browser@4).
            # The config sets content paths for class scanning. The CDN auto-scans
            # the rendered DOM, so content paths document what should be scanned
            # even though the browser CDN can only see the current page.
            result["js_tags"].append(_tailwind_config_script(theme_name, daisyui=daisyui, csp_nonce=csp_nonce))
            if daisyui:
                result["links"].append(_style_tag(
                    "https://cdn.jsdelivr.net/npm/daisyui@5"
                ))

    # Color theme CSS loads after framework CSS (Tailwind/DaisyUI) but before
    # miki.css. Sets --miki-* CSS variables that widgets rely on.
    # For plain mode, theme CSS is always loaded.
    # For Tailwind mode, theme CSS is also loaded to provide color variables.
    theme_css_url = None
    if theme.css_path and os.path.isfile(theme.css_path):
        theme_css_url = _theme_href(theme.css_path)
    elif effective_fw in (None, "css", "plain", "tailwind"):
        theme_css_url = f"/_miki/runtime/themes/{_esc(theme_name)}.css"

    if theme_css_url:
        result["links"].append(_style_tag(theme_css_url))

    # Body classes/data attributes
    extra = list(theme.extra_classes) or []
    data_attrs = ""
    if effective_fw == "tailwind":
        color_name = getattr(theme, "color_theme", None) or theme_name
        data_attrs = f' data-theme="{_esc(f"mikiui-{color_name}")}"'
    if extra:
        result["body_attrs"] = f' class="{_esc(" ".join(extra))}"{data_attrs}'
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

    theme_attr = f'data-miki-theme="{_esc(theme)}"'

    # Build the HEAD content
    theme_links = "\n".join(theme_data.get("links", []))
    inline = "\n".join(theme_data.get("inline_css", []))
    vars_css = theme_data.get("variables", "")

    scripts = _script_tags(runtime_scripts)

    # CSS Loading Strategy:
    # - miki.css contains base styles, @layer declarations, and widget styles.
    # - For Tailwind CDN: The Tailwind JS script must come first in <head> to
    #   process HTML and inject utility CSS. Tailwind's style attribute is added
    #   via a dedicated placeholder.
    # - For Tailwind Local / Plain: miki.css provides all widget styles.
    # - Widget-specific CSS (splitview, etc.) is discovered via static_assets.
    miki_css = _style_tag("/_miki/runtime/miki.css")
    all_links = f"{theme_links}\n{miki_css}"

    # Extract Tailwind CDN script if present (it should come before CSS)
    js_tags_list = theme_data.get("js_tags", [])
    tailwind_script = ""
    other_js_tags = ""
    if js_tags_list:
        all_js = "\n".join(js_tags_list)
        # If there's a Tailwind CDN script, put it first
        if "tailwindcss" in all_js:
            tailwind_script = all_js + "\n"
        else:
            other_js_tags = all_js + "\n"

    return BASE_TEMPLATE.format(
        html_lang=_esc(lang),
        page_title=_esc(title),
        favicon=favicon_tag,
        tailwind_script=tailwind_script,
        theme_links=all_links,
        theme_inline_css=inline,
        theme_vars=vars_css,
        theme_attr=theme_attr,
        body_class_attr=theme_data.get("body_attrs", ""),
        head_extra=head_extra,
        runtime_scripts=scripts,
        js_tags=other_js_tags,
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