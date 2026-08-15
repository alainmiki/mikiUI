"""Runtime CSS injection helpers for the MikiUI backend.

This module bridges the :class:`~mikiui.styling.system.StylingSystem` with
the HTML rendering layer.  It converts framework configs into the
``<link>`` / ``<style>`` tags injected into the page ``<head>``.

Mode handling:

* **dev mode** — Tailwind falls back to CDN so styles load immediately even
  before a local Tailwind build is set up.  Bootstrap uses the CDN.
  ``mikiui tailwind dev`` runs the watcher alongside the dev server.
* **prod mode** — Tailwind serves the compiled ``tailwind.css`` from
  ``_miki/runtime/themes/``.  Bootstrap CDN is still acceptable; for
  fully offline builds, users should switch to local mode.

Security note: no secrets or API keys are read or emitted here.
"""

from __future__ import annotations

from pathlib import Path

from .system import (
    BootstrapConfig,
    Framework,
    PlainCssConfig,
    StylingMode,
    StylingSystem,
    TailwindConfig,
    _bootstrap_runtime_html,
    _plain_runtime_html,
    _tailwind_runtime_html,
)


# ---------------------------------------------------------------------------
# Framework-aware CSS head block
# ---------------------------------------------------------------------------

def get_runtime_css(
    styling_system: "StylingSystem | None" = None,
    framework: str = "tailwind",
    mode: str = "dev",
    project_dir: str | Path = ".",
    **kwargs: Any,
) -> str:
    """Return the HTML for the ``<head>`` CSS injection block.

    This is the primary entry point used by the backend renderer.

    Parameters
    ----------
    styling_system:
        An optional :class:`~mikiui.styling.system.StylingSystem` instance.
        If provided, *framework* and *mode* are read from it.
    framework:
        One of ``"tailwind"``, ``"bootstrap"``, ``"plain"``.  Ignored if
        *styling_system* is given.
    mode:
        ``"dev"`` or ``"prod"``.  Ignored if *styling_system* is given.
    project_dir:
        Project root directory.
    **kwargs:
        Additional keyword arguments forwarded to the framework-specific
        HTML generators.

    Returns
    -------
    str
        HTML string suitable for injection into ``<head>`` (may be empty).
    """
    project_dir = Path(project_dir).resolve()

    if styling_system is not None:
        effective_mode = styling_system.mode
        effective_fw = styling_system.framework
    else:
        try:
            effective_mode = StylingMode(mode)
            effective_fw = Framework(framework)
        except ValueError:
            return ""

    if effective_fw == Framework.TAILWIND:
        config = (
            styling_system.tailwind_config
            if styling_system
            else kwargs.get("tailwind_config")
        )
        return _tailwind_runtime_html(config=config, mode=effective_mode, project_dir=project_dir)

    if effective_fw == Framework.BOOTSTRAP:
        config = (
            styling_system.bootstrap_config
            if styling_system
            else kwargs.get("bootstrap_config")
        )
        return _bootstrap_runtime_html(config=config, mode=effective_mode, project_dir=project_dir)

    config = (
        styling_system.plain_config
        if styling_system
        else kwargs.get("plain_config")
    )
    return _plain_runtime_html(config=config, project_dir=project_dir)


def css_head_block(
    framework: str = "tailwind",
    theme: str = "light",
    daisyui: bool = False,
    custom_css: list[str] | None = None,
    mode: str = "dev",
    runtime: str = "cdn",
    project_dir: str | Path = ".",
) -> str:
    """Convenience function: return a full ``<head>`` CSS block.

    Parameters
    ----------
    framework:
        CSS framework name.
    theme:
        Color theme name.
    daisyui:
        Enable DaisyUI (Tailwind only).
    custom_css:
        Extra CSS file paths.
    mode:
        ``"dev"`` or ``"prod"``.
    runtime:
        ``"cdn"`` or ``"local"``.  ``"cdn"`` uses public CDN URLs;
        ``"local"`` serves files from the project's ``_miki/runtime/`` dir.
    project_dir:
        Project root directory.

    Returns
    -------
    str
        HTML string ready for ``<head>`` injection.
    """
    from .bootstrap import BOOTSTRAP_CDN_CSS, BOOTSTRAP_CDN_JS

    custom_css = list(custom_css or [])
    project_dir = Path(project_dir).resolve()

    parts: list[str] = []

    if framework == "tailwind":
        use_cdn = runtime == "cdn" or mode == "dev"
        if use_cdn:
            cdn = "https://cdn.jsdelivr.net/npm/tailwindcss@3.4.1/dist/tailwind.min.css"
            parts.append(f'<link rel="stylesheet" href="{cdn}">')
            if daisyui:
                daisy_cdn = "https://cdn.jsdelivr.net/npm/daisyui@5/dist/daisyui.min.css"
                parts.append(f'<link rel="stylesheet" href="{daisy_cdn}">')
        else:
            tw = project_dir / "_miki" / "runtime" / "themes" / "tailwind.css"
            if tw.is_file():
                parts.append(f'<link rel="stylesheet" href="/_miki/runtime/themes/tailwind.css">')

    elif framework == "bootstrap":
        if runtime == "cdn" or mode == "dev":
            parts.append(f'<link rel="stylesheet" href="{BOOTSTRAP_CDN_CSS}">')
            parts.append(f'<script src="{BOOTSTRAP_CDN_JS}"></script>')
        else:
            local_css = project_dir / "static" / "bootstrap.min.css"
            if local_css.is_file():
                parts.append(f'<link rel="stylesheet" href="/static/bootstrap.min.css">')

    for css_path in custom_css:
        parts.append(f'<link rel="stylesheet" href="{css_path}">')

    return "\n    ".join(parts)


__all__ = [
    "get_runtime_css",
    "css_head_block",
]
