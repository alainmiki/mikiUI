"""Tailwind CSS v4 + DaisyUI v5 helpers for the MikiUI styling system.

This module is a thin facade over :mod:`mikiui.build.tailwind` that adds
Node.js detection, npm install orchestration, and user-facing messaging.
It does NOT duplicate the existing build logic.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def npm_dependencies(daisyui: bool = False) -> dict[str, str]:
    """Return the npm packages required for Tailwind v4 (+ optional DaisyUI v5)."""
    deps = {
        "tailwindcss": "^4.1.7",
    }
    if daisyui:
        deps["daisyui"] = "^5.0.0"
    return deps


def tailwind_config(
    theme: str = "light",
    daisyui: bool = False,
    content: list[str] | None = None,
    extend: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a complete Tailwind v4 configuration."""
    content_paths = list(content or []) + [
        "mikiui/runtime/miki.css",
        "mikiui/runtime/themes/*.css",
        "mikiui/components/**/*.py",
        "mikiui/widgets/**/*.py",
        "mikiui/build/tailwind/*.py", "mikiui/build/tailwind/**/*.py",
    ]

    config: dict[str, Any] = {
        "content": content_paths,
        "theme": {
            "extend": extend or {},
        },
        "plugins": [],
    }

    if daisyui:
        import os

        daisyui_path = os.path.join(
            os.path.dirname(__file__), "..", "runtime", "daisyui.min.js"
        )
        config["plugins"].append(f"'{daisyui_path}'")
        config["daisyui"] = {
            "themes": [daisyui_config(theme)],
            "base": True,
            "styled": True,
            "prefix": "miki-",
        }

    return config


def daisyui_config(theme: str = "dark") -> dict[str, Any]:
    """Build a DaisyUI v5 theme bridge from a MikiUI color theme."""
    from mikiui.themes import get_theme

    t = get_theme(theme)
    if t is None:
        raise ValueError(
            f"Unknown theme {theme!r}. Available: light, dark, dracula, solarized-dark"
        )

    css_text = t.css()
    import re

    daisy_theme: dict[str, str] = {}
    for match in re.finditer(r"--miki-(\w+):\s*([^;]+);", css_text):
        key = match.group(1)
        value = match.group(2).strip()
        daisy_theme[f"--{key}"] = value

    daisy_theme.setdefault("--primary", daisy_theme.get("--accent", "#3b82f6"))
    daisy_theme.setdefault("--secondary", daisy_theme.get("--accent-hover", "#60a5fa"))
    daisy_theme.setdefault("--background", daisy_theme.get("--bg", "#ffffff"))
    daisy_theme.setdefault("--foreground", daisy_theme.get("--fg", "#1e293b"))

    return {f"mikiui-{theme}": daisy_theme}


def write_config(
    path: str,
    theme: str = "light",
    daisyui: bool = False,
) -> str:
    """Write a ``tailwind.config.js`` for Tailwind v4."""
    import json

    from mikiui.build.tailwind import tailwind_config

    config = tailwind_config(theme=theme, daisyui=daisyui)

    if path.endswith(".js"):
        text = "export default "
        text += json.dumps(config, indent=2) + ";\n"
    elif path.endswith(".json"):
        text = json.dumps(config, indent=2) + "\n"
    else:
        text = json.dumps(config, indent=2) + "\n"

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return path


def write_postcss_config(path: str) -> str:
    """Write a ``postcss.config.js`` if one does not already exist."""
    p = Path(path)
    if p.is_file():
        return str(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        "export default {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n};\n",
        encoding="utf-8",
    )
    return str(p)


def install_deps(
    project_dir: str | Path,
    daisyui: bool = False,
) -> dict[str, Any]:
    """Write ``package.json`` (if needed) and run ``npm install``.

    Returns a report dict with ``status`` and ``message``.
    """
    import json
    import subprocess

    from .system import detect_node

    project_dir = Path(project_dir)
    pkg_json = project_dir / "package.json"

    deps = npm_dependencies(daisyui=daisyui)
    pkg: dict[str, Any] = {"name": "mikiui-styling", "version": "0.0.1", "private": True}
    if pkg_json.is_file():
        try:
            pkg = json.loads(pkg_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    pkg.setdefault("dependencies", {}).update(deps)
    pkg.setdefault("scripts", {})
    pkg["scripts"].setdefault("build:css", "mikiui tailwind build")
    pkg["scripts"].setdefault("dev:css", "mikiui tailwind dev")
    pkg_json.write_text(json.dumps(pkg, indent=2) + "\n", encoding="utf-8")

    node = detect_node()
    if not node.available:
        return {
            "status": "node_required",
            "message": (
                "Node.js is required for Tailwind CSS.\n"
                "  Install it from https://nodejs.org/\n"
                "  Then run 'npm install' in your project directory."
            ),
        }

    npm = subprocess.run(["npm", "install"], cwd=str(project_dir), capture_output=True, text=True)
    if npm.returncode != 0:
        return {
            "status": "error",
            "message": npm.stderr.strip() or "npm install failed.",
        }
    return {"status": "ok", "message": "npm install completed."}


def daisyui_bridge(theme_name: str = "light") -> dict[str, Any]:
    """Build a DaisyUI v5 theme bridge from a MikiUI color theme.

    Reads the CSS custom properties from the MikiUI theme and maps them
    to DaisyUI variable names.

    Parameters
    ----------
    theme_name:
        MikiUI theme name (e.g. ``"dark"``, ``"dracula"``).

    Returns
    -------
    dict[str, Any]
        A DaisyUI theme dict keyed by ``f"mikiui-{theme_name}"``.
    """
    from mikiui.themes import get_theme

    t = get_theme(theme_name)
    if t is None:
        raise ValueError(
            f"Unknown theme {theme_name!r}. Available: light, dark, dracula, solarized-dark"
        )

    css_text = t.css()
    import re

    daisy_theme: dict[str, str] = {}
    for match in re.finditer(r"--miki-(\w+):\s*([^;]+);", css_text):
        key = match.group(1)
        value = match.group(2).strip()
        daisy_theme[f"--{key}"] = value

    daisy_theme.setdefault("--primary", daisy_theme.get("--accent", "#3b82f6"))
    daisy_theme.setdefault("--secondary", daisy_theme.get("--accent-hover", "#60a5fa"))
    daisy_theme.setdefault("--background", daisy_theme.get("--bg", "#ffffff"))
    daisy_theme.setdefault("--foreground", daisy_theme.get("--fg", "#1e293b"))

    return {f"mikiui-{theme_name}": daisy_theme}


__all__ = ["npm_dependencies", "write_config", "write_postcss_config", "install_deps", "daisyui_bridge"]
