"""Web build for MikiUI (fullstack / separate modes).

Produces a real, shippable artifact (no placeholders): renders every GET route
to a static HTML file, copies the vendored runtime assets next to them, and
(``fullstack`` mode) emits a small ASGI server so the build can be served as a
standalone app. ``separate`` mode emits only the static front-end.

The build also generates:
- A production HTML shell with proper CSP nonces and meta tags.
- A ``manifest.json`` with content hashes for cache busting.
- A ``sitemap.xml`` for crawler discoverability.
"""

from __future__ import annotations

import asyncio
import hashlib
import html as _html
import json
import os
import shutil
import warnings
from typing import Any

from ..app.routes import RouteDef
from ..engine.renderer import render_page

# Runtime assets that must ship with a static build (all offline, no CDN).
_RUNTIME_ASSETS = (
    "htmx.min.js",
    "alpine.min.js",
    "htmx_runtime.js",
    "alpine_runtime.js",
    "miki_ui.js",
    "miki.css",
    "history_router.js",
)
_RUNTIME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runtime"))


def _esc(value: Any) -> str:
    """Escape a value for safe insertion into HTML."""
    return _html.escape(str(value), quote=True)


def _generate_csp_nonce(length: int = 16) -> str:
    """Generate a random CSP nonce string."""
    import base64
    import secrets

    return base64.b64encode(secrets.token_bytes(length)).decode("ascii")


def _file_hash(path: str) -> str | None:
    """Return a short SHA-256 hex digest for *path*, or ``None`` on error."""
    try:
        sha = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                sha.update(chunk)
        return sha.hexdigest()[:16]
    except Exception:
        return None


def _route_filename(path: str) -> str:
    if path in ("", "/"):
        return "index.html"
    clean = path.strip("/").replace("/", "_")
    return f"{clean}.html"


def _has_path_params(route: RouteDef) -> bool:
    return bool(route.path_params)


def _render_sitemap(app: Any, out_dir: str, pages: list[str]) -> str | None:
    """Write a ``sitemap.xml`` for all rendered pages."""
    if not pages:
        return None
    base_url = f"http://{getattr(app, 'host', 'localhost')}:{getattr(app, 'port', 8000)}"
    url_entries = []
    for page in pages:
        if page == "index.html":
            loc = base_url + "/"
        else:
            loc = base_url + "/" + page.replace("_", "/").replace(".html", "")
        url_entries.append(f"  <url><loc>{_esc(loc)}</loc></url>")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(url_entries)
        + "\n</urlset>\n"
    )
    dest = os.path.join(out_dir, "sitemap.xml")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(xml)
    return dest


def _load_route_manifest(out_dir: str) -> dict[str, list[str]] | None:
    """Load ``route-manifest.json`` from *out_dir* if present.

    The manifest maps route paths to example path-param values for static
    export of parameterized routes:

    {
      "/users/{user_id}": ["1", "42", "99"]
    }

    Returns ``None`` if the file does not exist or is invalid.
    """
    manifest_path = os.path.join(out_dir, "route-manifest.json")
    if not os.path.isfile(manifest_path):
        return None
    try:
        with open(manifest_path, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if isinstance(v, list)}
    except Exception:
        pass
    return None


def _render_parameterized_routes(
    miki_app: Any,
    out_dir: str,
    *,
    theme: str = "light",
    framework: str | None = None,
    style_mode: str = "cdn",
    daisyui: bool = False,
    nonce: str | None = None,
) -> list[str]:
    """Render parameterized routes using example paths from route-manifest.json."""
    manifest = _load_route_manifest(out_dir)
    if not manifest:
        return []

    written: list[str] = []
    for route in miki_app.routes.values():
        if not _has_path_params(route) or "GET" not in route.methods:
            continue
        examples = manifest.get(route.path, [])
        if not examples:
            continue
        param_names = list(route.path_params)
        for example in examples:
            try:
                resolved_path = route.path
                params: dict[str, str] = {}
                if isinstance(example, list):
                    values = [str(v) for v in example]
                else:
                    values = [str(example)] * len(param_names)
                for key, val in zip(param_names, values):
                    params[key] = val
                    resolved_path = resolved_path.replace("{" + key + "}", val)
                nodes, ctx = asyncio.run(miki_app.invoke(route, None, path_params=params))
                from ..app.routes import resolve_title

                page_title = resolve_title(route, ctx, miki_app.title)
                head_extra = miki_app.head_extra_html()
                favicon = miki_app.favicon
                html = render_page(
                    nodes,
                    title=page_title,
                    lang=miki_app.lang,
                    theme=theme,
                    framework=framework,
                    style_mode=style_mode,
                    daisyui=daisyui,
                    favicon=favicon,
                    head_extra=head_extra,
                    csp_nonce=nonce,
                )
                if nonce:
                    html = html.replace("<script ", f'<script nonce="{_esc(nonce)}" ')
                    html = html.replace("<style ", f'<style nonce="{_esc(nonce)}" ')
                html = html.replace('"/_miki/runtime/', '"_miki/runtime/')
                dest = os.path.join(out_dir, _route_filename(resolved_path))
                with open(dest, "w", encoding="utf-8") as fh:
                    fh.write(html)
                written.append(os.path.relpath(dest, out_dir))
            except Exception as exc:
                warnings.warn(
                    f"Skipping parameterized route {route.path} with example {example}: {exc}"
                )
    return written


def _export_route(
    miki_app: Any,
    route: RouteDef,
    out_dir: str,
    *,
    theme: str = "light",
    framework: str | None = None,
    style_mode: str = "cdn",
    daisyui: bool = False,
    nonce: str | None = None,
) -> str | None:
    """Render a single GET route to ``out_dir``. Returns the file path or None."""
    if "GET" not in route.methods:
        return None
    if _has_path_params(route):
        warnings.warn(
            f"Skipping static export of parameterized route {route.path!r}. "
            "Static builds cannot render dynamic routes; use fullstack mode "
            "or provide example paths via route-manifest.json."
        )
        return None
    try:
        nodes, ctx = asyncio.run(miki_app.invoke(route, None))
    except Exception as exc:
        warnings.warn(f"Skipping static export of {route.path}: {exc}")
        return None
    from ..app.routes import resolve_title

    page_title = resolve_title(route, ctx, miki_app.title)
    head_extra = miki_app.head_extra_html()
    favicon = miki_app.favicon
    html = render_page(
        nodes,
        title=page_title,
        lang=miki_app.lang,
        theme=theme,
        framework=framework,
        style_mode=style_mode,
        daisyui=daisyui,
        favicon=favicon,
        head_extra=head_extra,
        csp_nonce=nonce,
    )
    if nonce:
        html = html.replace("<script ", f'<script nonce="{_esc(nonce)}" ')
        html = html.replace("<style ", f'<style nonce="{_esc(nonce)}" ')
    html = html.replace('"/_miki/runtime/', '"_miki/runtime/')
    dest = os.path.join(out_dir, _route_filename(route.path))
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(html)
    return dest


def _build_tailwind(
    app: Any,
    *,
    out_dir: str,
    daisyui: bool = False,
    ext: dict[str, Any] | None = None,
    content: list[str] | None = None,
) -> str | None:
    """Run Tailwind JIT to generate CSS. Returns the path to the output file."""
    import subprocess
    import tempfile

    from .tailwind import write_tailwind_config

    css_path = os.path.join(out_dir, "_miki", "runtime", "mikiui.css")
    os.makedirs(os.path.dirname(css_path), exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        write_tailwind_config(
            os.path.join(tmpdir, "tailwind.config.js"),
            theme=getattr(app, "theme", "light"),
            daisyui=daisyui,
            content=content,
            extend=ext,
        )

        cmd = [
            "npx",
            "tailwindcss",
            "-i",
            "mikiui/runtime/miki.css",
            "-o",
            css_path,
            "--content",
        ]
        cmd.extend(_CONTENT_PATHS)

        proc = subprocess.run(cmd, cwd=os.getcwd(), capture_output=True, text=True)
        if proc.returncode != 0:
            import warnings

            warnings.warn(f"Tailwind build failed: {proc.stderr}")
            return None
        if os.path.isfile(css_path):
            return css_path
    return None


_CONTENT_PATHS = [
    "mikiui/runtime/miki.css",
    "mikiui/runtime/themes/*.css",
    "mikiui/components/**/*.py",
    "mikiui/widgets/**/*.py",
    "mikiui/build/tailwind/**/*.py",
]


def _write_server_script(out_dir: str, app: Any) -> str:
    """Emit a small ASGI server so a fullstack build is runnable standalone."""
    spec = f"{app.__module__}:{_attr_name(app)}"
    script = (
        "import uvicorn\n"
        "from mikiui.backend import create_app\n"
        "from mikiui.app import MikiApp\n"
        "\n"
        f"_APP_SPEC = {spec!r}\n"
        "def _load():\n"
        "    import importlib\n"
        "    mod_name, _, attr = _APP_SPEC.partition(':')\n"
        "    return getattr(importlib.import_module(mod_name), attr or 'app')\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    miki_app = _load()\n"
        "    uvicorn.run(create_app(miki_app), host='127.0.0.1', port=8000)\n"
    )
    dest = os.path.join(out_dir, "server.py")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(script)
    return "server.py"


def _write_html_shell(
    out_dir: str,
    *,
    title: str,
    lang: str = "en",
    theme: str = "light",
    framework: str | None = None,
    style_mode: str = "cdn",
    daisyui: bool = False,
    nonce: str | None = None,
    favicon: str | None = None,
    csp: str | None = None,
) -> str:
    """Write a production HTML shell to ``out_dir/index.html``.

    The shell includes CSP meta tags, proper charset/viewport, and a minimal
    body that bootstraps the MikiUI runtime. Returns the file path.
    """
    nonce_attr = f' nonce="{_esc(nonce)}"' if nonce else ""
    csp_meta = f'<meta http-equiv="Content-Security-Policy" content="{_esc(csp)}" />' if csp else ""
    favicon_tag = f'<link rel="icon" href="{_esc(favicon)}" type="image/png" />' if favicon else ""

    effective_fw = framework or "plain"
    if effective_fw == "tailwind":
        if style_mode == "local":
            css_link = f'<link rel="stylesheet" href="_miki/runtime/themes/tailwind.css"{nonce_attr} />'
            if daisyui:
                css_link += (
                    f'\n  <link rel="stylesheet" '
                    f'href="https://cdn.jsdelivr.net/npm/daisyui@5/dist/daisyui.css"'
                    f'{nonce_attr} />'
                )
        else:
            css_link = '<script src="https://cdn.tailwindcss.com"></script>'
            if daisyui:
                css_link += (
                    f'\n  <link rel="stylesheet" '
                    f'href="https://cdn.jsdelivr.net/npm/daisyui@5/dist/daisyui.css"'
                    f'{nonce_attr} />'
                )
        body_attr = f'data-theme="mikiui-{_esc(theme)}"'
    else:
        css_link = f'<link rel="stylesheet" href="_miki/runtime/miki.css"{nonce_attr} />'
        body_attr = f'data-miki-theme="{_esc(theme)}"'

    shell = f"""<!doctype html>
<html lang="{_esc(lang)}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{_esc(title)}" />
  {csp_meta}
  {favicon_tag}
  <title>{_esc(title)}</title>
  {css_link}
</head>
<body {body_attr}>
  <div id="miki-app"></div>
  <script src="_miki/runtime/htmx.min.js"{nonce_attr} defer></script>
  <script src="_miki/runtime/alpine.min.js"{nonce_attr} defer></script>
  <script src="_miki/runtime/miki_ui.js"{nonce_attr} defer></script>
</body>
</html>
"""
    dest = os.path.join(out_dir, "index.html")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(shell)
    return dest


def _write_manifest(out_dir: str, asset_paths: dict[str, str]) -> str | None:
    """Write a ``manifest.json`` with content hashes for cache busting.

    Parameters
    ----------
    out_dir:
        Directory where ``manifest.json`` will be written.
    asset_paths:
        Mapping of logical asset name to relative file path.

    Returns
    -------
    str or None
        The path to ``manifest.json``, or ``None`` if no assets were hashed.
    """
    if not asset_paths:
        return None
    manifest: dict[str, Any] = {"version": "1.0", "files": {}}
    for logical_name, rel_path in asset_paths.items():
        abs_path = os.path.join(out_dir, rel_path)
        digest = _file_hash(abs_path)
        if digest:
            manifest["files"][logical_name] = {"path": rel_path, "hash": f"sha256-{digest}"}
    if not manifest["files"]:
        return None
    dest = os.path.join(out_dir, "manifest.json")
    import json

    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    return dest


def _attr_name(app: Any) -> str:
    for name, val in vars(type(app)).items():
        if val is app:
            return str(name)
    # Fall back to scanning the module for the instance.
    import sys

    mod = sys.modules.get(getattr(app, "__module__", ""))
    if mod:
        for name, val in vars(mod).items():
            if val is app:
                return str(name)
    return "app"


def build_web(
    app: Any,
    *,
    mode: str = "fullstack",
    out_dir: str = "dist",
    theme: str | None = None,
    framework: str | None = None,
    style_mode: str = "cdn",
    daisyui: bool = False,
    tailwind_ext: dict[str, Any] | None = None,
    tailwind_content: list[str] | None = None,
    skip_tailwind: bool = False,
    concurrency: int = 4,
) -> dict[str, Any]:
    """Build a web target.

    ``mode`` is ``"fullstack"`` (static export + ASGI server script) or
    ``"separate"`` (static front-end only). Returns a build report.

    ``theme`` - Color theme name (e.g. "light", "dark", "dracula").

    ``framework`` - Styling framework: ``"plain"`` or ``"tailwind"``.
    If ``None``, falls back to ``app.style_framework`` or ``"plain"``.

    ``style_mode`` - Tailwind only. ``"cdn"`` uses public CDN; ``"local"``
    serves a locally built CSS file.

    ``daisyui`` - Enable DaisyUI plugin when building with Tailwind.

    ``tailwind_ext`` / ``tailwind_content`` - Additional Tailwind config options.

    ``concurrency`` - Number of parallel route renders.

    The build report includes:

    * ``pages`` — list of rendered HTML file paths (relative to ``out_dir``).
    * ``runtime_assets`` — list of copied runtime files.
    * ``manifest`` — path to ``manifest.json`` (if generated), or ``None``.
    * ``shell`` — path to the production HTML shell.
    * ``sitemap`` — path to ``sitemap.xml``, or ``None``.
    * ``csp_nonce`` — the nonce embedded in the shell (or ``None``).
    * ``server_script`` — path to ``server.py`` in fullstack mode, or ``None``.
    * ``skipped_routes`` — list of parameterized routes skipped with warnings.
    """
    if mode not in ("fullstack", "separate"):
        raise ValueError(f"Invalid web build mode: {mode}")
    if not hasattr(app, "routes"):
        raise TypeError("build_web expects a MikiApp instance")

    os.makedirs(out_dir, exist_ok=True)

    # Resolve framework from explicit param or app defaults
    effective_framework = framework or getattr(app, "style_framework", None) or "plain"
    effective_style_mode = getattr(app, "style_mode", "cdn") if style_mode == "cdn" else style_mode
    effective_daisyui = bool(getattr(app, "style_daisyui", False) or daisyui)

    # Handle Tailwind build
    tailwind_css_path = None
    if effective_framework == "tailwind" and not skip_tailwind:
        tailwind_css_path = _build_tailwind(
            app=app,
            out_dir=out_dir,
            daisyui=effective_daisyui,
            ext=tailwind_ext,
            content=tailwind_content,
        )

    written: list[str] = []
    skipped_routes: list[str] = []

    async def _render_all() -> list[str]:
        results: list[str] = []
        semaphore = asyncio.Semaphore(concurrency)

        async def _render(route: RouteDef) -> str | None:
            async with semaphore:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    lambda: _export_route(
                        app, route, out_dir,
                        theme=actual_theme,
                        framework=effective_framework,
                        style_mode=effective_style_mode,
                        daisyui=effective_daisyui,
                        nonce=nonce,
                    ),
                )

        tasks = [_render(route) for route in app.routes.values()]
        for coro in asyncio.as_completed(tasks):
            path = await coro
            if path:
                results.append(os.path.relpath(path, out_dir))
        return results

    actual_theme: str = theme if theme is not None else (getattr(app, "theme", None) or "light")
    nonce = _generate_csp_nonce()

    try:
        written = asyncio.run(_render_all())
    except RuntimeError:
        for route in app.routes.values():
            path = _export_route(
                app, route, out_dir,
                theme=actual_theme,
                framework=effective_framework,
                style_mode=effective_style_mode,
                daisyui=effective_daisyui,
                nonce=nonce,
            )
            if path:
                written.append(os.path.relpath(path, out_dir))

    for route in app.routes.values():
        if _has_path_params(route) and "GET" in route.methods:
            skipped_routes.append(route.path)

    # Render parameterized routes if a route-manifest.json is present
    param_written = _render_parameterized_routes(
        app, out_dir,
        theme=actual_theme,
        framework=effective_framework,
        style_mode=effective_style_mode,
        daisyui=effective_daisyui,
        nonce=nonce,
    )
    written.extend(param_written)

    runtime_out = os.path.join(out_dir, "_miki", "runtime")
    os.makedirs(runtime_out, exist_ok=True)
    copied: list[str] = []

    def _copy_runtime_assets(include_miki_css: bool = True) -> None:
        """Copy runtime assets, including subdirectories like js/."""
        for entry in os.listdir(_RUNTIME_DIR):
            src = os.path.join(_RUNTIME_DIR, entry)
            if entry in ("__pycache__",):
                continue
            if src.endswith(".py"):
                continue
            dst = os.path.join(runtime_out, entry)
            if os.path.isdir(src):
                # Copy entire subdirectory (e.g., js/, themes/)
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                copied.append(entry + "/")
            elif os.path.isfile(src):
                if entry == "miki.css" and not include_miki_css:
                    continue
                shutil.copy2(src, dst)
                copied.append(entry)

    if effective_framework == "tailwind":
        _copy_runtime_assets(include_miki_css=False)
    else:
        _copy_runtime_assets(include_miki_css=True)

    # If Tailwind was built, copy the CSS file
    if tailwind_css_path:
        dest_css = os.path.join(runtime_out, "mikiui.css")
        shutil.copy2(tailwind_css_path, dest_css)
        copied.append("mikiui.css")

    # Copy component/widget/plugin/theme static assets so the exported site
    # is self-contained.
    static_manifest_entries: dict[str, str] = {}
    for root_type in ("components", "widgets"):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", root_type))
        if not os.path.isdir(root_dir):
            continue
        for pkg in os.listdir(root_dir):
            static_src = os.path.join(root_dir, pkg, "static")
            if not os.path.isdir(static_src):
                continue
            static_dst = os.path.join(out_dir, "_miki", root_type, pkg, "static")
            os.makedirs(static_dst, exist_ok=True)
            for fname in os.listdir(static_src):
                src_file = os.path.join(static_src, fname)
                if os.path.isfile(src_file):
                    dst_file = os.path.join(static_dst, fname)
                    shutil.copy2(src_file, dst_file)
                    rel = os.path.relpath(dst_file, out_dir)
                    key = f"{root_type}/{pkg}/{fname}"
                    static_manifest_entries[key] = rel

    # Also include theme static files (color theme CSS files in runtime/themes)
    themes_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runtime", "themes"))
    if os.path.isdir(themes_src):
        themes_dst = os.path.join(out_dir, "_miki", "runtime", "themes")
        os.makedirs(themes_dst, exist_ok=True)
        for fname in os.listdir(themes_src):
            if fname.endswith(".css"):
                src_file = os.path.join(themes_src, fname)
                if os.path.isfile(src_file):
                    dst_file = os.path.join(themes_dst, fname)
                    shutil.copy2(src_file, dst_file)
                    rel = os.path.relpath(dst_file, out_dir)
                    key = f"themes/{fname}"
                    static_manifest_entries[key] = rel

    # Generate CSP nonce and HTML shell
    # For Tailwind CDN mode, allow CDN styles
    if effective_framework == "tailwind" and effective_style_mode == "cdn":
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net; "
            "style-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'".replace("{nonce}", nonce)
        )
    else:
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'nonce-{nonce}'; "
            "style-src 'self' 'nonce-{nonce}'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'".replace("{nonce}", nonce)
        )

    shell_path = _write_html_shell(
        out_dir,
        title=app.title,
        lang=app.lang,
        theme=actual_theme,
        framework=effective_framework,
        style_mode=effective_style_mode,
        daisyui=effective_daisyui,
        nonce=nonce,
        favicon=app.favicon,
        csp=csp,
    )

    # Manifest with hashes
    asset_rel_paths: dict[str, str] = {
        name: "/".join(["_miki", "runtime", name]) for name in copied
    }
    asset_rel_paths.update(static_manifest_entries)
    manifest_path = _write_manifest(out_dir, asset_rel_paths)

    # Sitemap
    sitemap_path = _render_sitemap(app, out_dir, written)

    server_script = None
    if mode == "fullstack":
        server_script = _write_server_script(out_dir, app)

    return {
        "target": "web",
        "mode": mode,
        "out_dir": out_dir,
        "pages": written,
        "runtime_assets": copied,
        "manifest": manifest_path,
        "shell": shell_path,
        "sitemap": sitemap_path,
        "csp_nonce": nonce,
        "server_script": server_script,
        "tailwind_built": tailwind_css_path is not None,
        "skipped_routes": skipped_routes,
        "parameterized_pages": param_written,
        "route_manifest_used": bool(param_written),
        "status": "ok",
    }
