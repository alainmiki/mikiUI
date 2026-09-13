"""Tailwind CSS v4 + DaisyUI v5 integration for MikiUI.

This module provides utilities to generate a Tailwind v4 configuration that
composes MikiUI's default styles with DaisyUI component classes.

The integration is **opt-in**: MikiUI works perfectly fine with the bundled
``miki.css`` for offline use.  When Tailwind is configured, the generated
config pulls in:

* MikiUI's own CSS classes (so ``miki-btn``, ``miki-input``, etc. get
  Tailwind's JIT compiler and can be purged for minimal bundles).
* DaisyUI (if enabled) with the currently selected theme.
* Any user-supplied ``tailwind.config.*`` overrides.

Usage in a build::

    from mikiui.build.tailwind import tailwind_config, daisyui_config

    config = tailwind_config(theme="dark", daisyui=True)
    print(json.dumps(config, indent=2))

See: https://tailwindcss.com / https://daisyui.com
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ...themes import THEME_DIR, Theme, get_theme, list_themes

#: MikiUI CSS class prefixes that the Tailwind JIT should scan for.
MIKI_PREFIXES = ["miki-"]


def _miki_utilities() -> list[str]:
    """Return a list of MikiUI utility-class patterns for Tailwind's safelist."""
    return [
        "miki-btn",
        "miki-btn-primary",
        "miki-btn-secondary",
        "miki-btn-ghost",
        "miki-btn-sm",
        "miki-btn-lg",
        "miki-input",
        "miki-input-filled",
        "miki-input-sm",
        "miki-input-lg",
        "miki-checkbox",
        "miki-radio",
        "miki-slider",
        "miki-select",
        "miki-fieldset",
        "miki-legend",
        "miki-label",
        "miki-form",
        "miki-form-inline",
        "miki-table",
        "miki-table-striped",
        "miki-th",
        "miki-td",
        "miki-caption",
        "miki-dialog",
        "miki-details",
        "miki-summary",
        "miki-progress",
        "miki-progress-striped",
        "miki-meter",
        "miki-output",
        "miki-filepicker",
        "miki-file-label",
        "miki-file-input",
        "miki-filepicker-name",
        "miki-chart",
        "miki-chart-bar",
        "miki-chart-line",
        "miki-chart-slice",
        "miki-chart-empty",
        "miki-tab",
        "miki-tab-active",
        "miki-tablist",
        "miki-tabs",
        "miki-listview",
        "miki-treeview",
        "miki-calendar",
        "miki-calendar-caption",
        "miki-modal",
        "miki-modal-overlay",
        "miki-modal-panel",
        "miki-text-muted",
        "miki-text-secondary",
        "miki-bg-surface",
        "miki-border",
    ]


def daisyui_config(theme: str = "dark") -> dict[str, Any]:
    """Generate a DaisyUI v5 theme configuration block.

    DaisyUI themes are maps of CSS variables.  We bridge MikiUI's theme
    system by providing a theme named ``"mikiui-{name}"`` for each registered
    MikiUI theme.
    """
    t = get_theme(theme)
    if t is None:
        raise ValueError(f"Unknown theme: {theme!r}. Available: {', '.join(list_themes())}")

    css = t.css()
    daisyui_theme: dict[str, Any] = {}

    import re

    for match in re.finditer(r"--miki-(\w+):\s*([^;]+);", css):
        key = match.group(1)
        value = match.group(2).strip()
        daisyui_theme[f"--{key}"] = value

    daisyui_theme.setdefault("--primary", daisyui_theme.get("--accent", "#3b82f6"))
    daisyui_theme.setdefault("--secondary", daisyui_theme.get("--accent-hover", "#60a5fa"))
    daisyui_theme.setdefault("--background", daisyui_theme.get("--bg", "#ffffff"))
    daisyui_theme.setdefault("--foreground", daisyui_theme.get("--fg", "#1e293b"))

    return {f"mikiui-{theme}": daisyui_theme}


def _resolve_daisyui_plugin_path() -> str | None:
    """Return the filesystem path to the DaisyUI v5 Tailwind plugin JS.

    Checks the bundled runtime first, then the project's ``node_modules``.
    Returns ``None`` if the plugin cannot be found.
    """
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "runtime", "daisyui.min.js"),
        os.path.join(os.getcwd(), "node_modules", "daisyui", "dist", "daisyui.min.js"),
        os.path.join(os.getcwd(), "node_modules", "daisyui", "daisyui.min.js"),
    ]
    for candidate in candidates:
        candidate = os.path.abspath(candidate)
        if os.path.isfile(candidate):
            return candidate
    return None


def tailwind_config(
    theme: str = "light",
    daisyui: bool = False,
    content: list[str] | None = None,
    extend: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a complete Tailwind v4 configuration.

    Parameters
    ----------
    theme:
        The active MikiUI theme name (controls DaisyUI theme if enabled).
    daisyui:
        If ``True``, includes the DaisyUI plugin and generates a theme bridge.
    content:
        Additional file globs to scan for classes (beyond MikiUI defaults).
    extend:
        Arbitrary dict merged into the Tailwind config under ``theme.extend``.
    """
    content_paths = list(content or []) + [
        "mikiui/runtime/miki.css",
        "mikiui/runtime/themes/*.css",
        "mikiui/components/**/*.py",
        "mikiui/widgets/**/*.py",
        "mikiui/build/tailwind/*.py",
        "mikiui/build/tailwind/**/*.py",
    ]

    config: dict[str, Any] = {
        "content": content_paths,
        "theme": {
            "extend": extend or {},
        },
        "plugins": [],
    }

    if daisyui:
        daisyui_path = _resolve_daisyui_plugin_path()
        if daisyui_path is None:
            import warnings

            warnings.warn(
                "DaisyUI plugin not found. "
                "Run 'mikiui install tailwind daisyui' to install npm dependencies, "
                "or use Tailwind CDN mode (no local build required). "
                "Falling back to Tailwind without DaisyUI."
            )
        else:
            config["plugins"].append(f"'{daisyui_path}'")
            config["daisyui"] = {
                "themes": [daisyui_config(theme)],
                "base": True,
                "styled": True,
                "prefix": "miki-",
            }

    return config


def write_tailwind_config(
    path: str,
    theme: str = "light",
    daisyui: bool = False,
    content: list[str] | None = None,
    extend: dict[str, Any] | None = None,
) -> str:
    """Write a ``tailwind.config.js`` file and return its path.

    If the file already exists, user customizations are preserved by merging
    the generated config with the existing one.
    """
    generated = tailwind_config(
        theme=theme, daisyui=daisyui, content=content, extend=extend
    )

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    existing: dict[str, Any] | None = None
    if p.is_file():
        text = p.read_text(encoding="utf-8")
        existing = _parse_tailwind_config(text)

    config = _merge_tailwind_config(existing, generated)

    if path.endswith(".js"):
        text = "export default "
        text += json.dumps(config, indent=2) + ";\n"
    elif path.endswith(".json"):
        text = json.dumps(config, indent=2) + "\n"
    else:
        text = json.dumps(config, indent=2) + "\n"

    p.write_text(text, encoding="utf-8")
    return path


def _parse_tailwind_config(text: str) -> dict[str, Any] | None:
    """Parse a tailwind.config.js or .json file into a dict."""
    import re
    from typing import cast

    # Try to extract JSON from `export default ...` or `module.exports = ...`
    m = re.search(r"export\s+default\s+(\{.*\});?\s*$", text, re.DOTALL)
    if not m:
        m = re.search(r"module\.exports\s*=\s*(\{.*\});?\s*$", text, re.DOTALL)
    if m:
        try:
            return cast(dict[str, Any], json.loads(m.group(1)))
        except (json.JSONDecodeError, ValueError):
            return None

    # Try parsing the whole text as JSON
    try:
        return cast(dict[str, Any], json.loads(text))
    except (json.JSONDecodeError, ValueError):
        return None


def _merge_tailwind_config(
    existing: dict[str, Any] | None,
    generated: dict[str, Any],
) -> dict[str, Any]:
    """Merge an existing Tailwind config with a newly generated one.

    User customizations in ``existing`` are preserved.  The ``generated``
    config provides defaults and takes precedence for known keys, but any
    extra keys in ``existing`` are retained.
    """
    if not existing:
        return generated

    merged = dict(existing)

    # content: merge and deduplicate
    gen_content = generated.get("content", [])
    existing_content = merged.get("content", [])
    if isinstance(gen_content, list) and isinstance(existing_content, list):
        merged["content"] = list(dict.fromkeys(existing_content + gen_content))

    # theme.extend: deep merge
    gen_extend = generated.get("theme", {}).get("extend", {})
    existing_theme = merged.get("theme", {})
    if isinstance(existing_theme, dict):
        existing_extend = existing_theme.get("extend", {})
        if isinstance(gen_extend, dict) and isinstance(existing_extend, dict):
            merged_extend = dict(existing_extend)
            merged_extend.update(gen_extend)
            merged_theme = dict(existing_theme)
            merged_theme["extend"] = merged_extend
            merged["theme"] = merged_theme

    # plugins: merge and deduplicate
    gen_plugins = generated.get("plugins", [])
    existing_plugins = merged.get("plugins", [])
    if isinstance(gen_plugins, list) and isinstance(existing_plugins, list):
        merged_plugins = list(dict.fromkeys(existing_plugins + gen_plugins))
        merged["plugins"] = merged_plugins

    # daisyui: preserve existing if present, otherwise use generated
    if "daisyui" not in merged and "daisyui" in generated:
        merged["daisyui"] = generated["daisyui"]

    # Preserve any extra keys from generated that are not in existing
    for key, value in generated.items():
        if key not in merged:
            merged[key] = value

    return merged


def component_library_link(name: str) -> str:
    """Return a CDN link for a well-known component library.

    Supported: ``"daisyui"``, ``"preload"`` (font preload).
    """
    links = {
        "daisyui": '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/daisyui@5/dist/daisyui.css">',
        "preload": '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">',
    }
    return links.get(name, "")


def build_css(
    theme: str = "light",
    daisyui: bool = False,
    out: str | None = None,
    optimize: bool = True,
    watch: bool = False,
    content: list[str] | None = None,
) -> str:
    """Build a CSS file using Tailwind v4 (or fallback to miki.css).

    This is a simplified build that works when Tailwind CLI v4 is available,
    otherwise falls back to copying the bundled miki.css.

    Parameters
    ----------
    theme : str
        The active MikiUI color theme name.
    daisyui : bool
        Whether to enable DaisyUI plugin.
    out : str | None
        Output path for the CSS file. If None, uses a temp file path.
    optimize : bool
        Whether to minify the output.
    watch : bool
        Whether to watch for changes and rebuild (dev mode).
    content : list[str] | None
        Extra content paths to scan for Tailwind classes.

    Returns
    -------
    str
        The CSS file path.

    Raises
    ------
    RuntimeError
        If Node.js is not available and a Tailwind build is requested.
    """
    from ...themes import get_theme

    t = get_theme(theme)

    config = tailwind_config(theme=theme, daisyui=daisyui, content=content)

    import json
    import shutil
    import subprocess
    import tempfile

    config_fh = tempfile.NamedTemporaryFile(delete=False, suffix=".js", mode="w", encoding="utf-8")
    config_path = config_fh.name
    try:
        config_fh.write("export default " + json.dumps(config) + ";\n")
    finally:
        config_fh.close()

    css_path = os.path.join(os.path.dirname(__file__), "..", "..", "runtime", "miki.css")
    css_path = os.path.abspath(css_path)

    result_path = out or os.path.join(THEME_DIR, "tailwind.css")

    node_available = shutil.which("npx") is not None
    tailwind_available = False
    if node_available:
        try:
            check = subprocess.run(
                ["npx", "--yes", "tailwindcss", "--help"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            tailwind_available = check.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            tailwind_available = False

    if not tailwind_available:
        if node_available:
            import warnings

            warnings.warn(
                "Node.js is available but 'npx tailwindcss' failed. "
                "Falling back to bundled miki.css. "
                "Install Tailwind CSS CLI v4 with: npm install -g tailwindcss"
            )
        else:
            import warnings

            warnings.warn(
                "Node.js is not available (npx not found). "
                "Falling back to bundled miki.css. "
                "Install Node.js from https://nodejs.org/ to enable Tailwind builds."
            )
        shutil.copy2(css_path, result_path)
        if not watch:
            try:
                os.unlink(config_path)
            except OSError:
                pass
        if t:
            t.css_path = result_path
        return result_path

    try:
        cmd = [
            "npx", "tailwindcss",
            "-i", css_path,
            "-o", result_path,
            "-c", config_path,
        ]
        if watch:
            cmd.append("--watch")
        subprocess.run(cmd, check=True, capture_output=True)
        if watch:
            return result_path
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Tailwind CSS v4 CLI not found. "
            "Install it with: npm install -g tailwindcss"
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Tailwind CSS build failed (exit {exc.returncode}): {exc.stderr}"
        ) from exc
    finally:
        if not watch:
            try:
                os.unlink(config_path)
            except OSError:
                pass

    if optimize and not watch:
        try:
            with open(result_path) as f:
                text = f.read()
            minified = "\n".join(line.rstrip() for line in text.splitlines() if line.strip())
            with open(result_path, "w") as f:
                f.write(minified)
        except Exception:
            pass

    if t:
        t.css_path = result_path

    return result_path


def register_built_theme(
    name: str,
    css_path: str,
    daisyui: bool = False,
    variables: dict[str, str] | None = None,
) -> None:
    """Register a built CSS theme (e.g., from a Tailwind build).

    Parameters
    ----------
    name : str
        Theme name to register.
    css_path : str
        Path to the built CSS file.
    daisyui : bool
        Whether to enable DaisyUI for this theme.
    variables : dict
        Optional CSS custom property overrides.
    """
    from ...themes import register_theme

    theme = Theme(
        name=name,
        source="builtin-framework",
        framework="tailwind" if daisyui else "css",
        css_path=css_path,
        variables=variables or {},
    )
    register_theme(theme)


__all__ = [
    "tailwind_config",
    "daisyui_config",
    "write_tailwind_config",
    "component_library_link",
    "build_css",
    "register_built_theme",
    "MIKI_PREFIXES",
]
