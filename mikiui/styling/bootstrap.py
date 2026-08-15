"""Bootstrap CSS helpers for the MikiUI styling system.

This module is a thin facade over the theme system.  Bootstrap is loaded
from the jsDelivr CDN by default; users can switch to local files by
setting paths on their ``MikiApp``.
"""

from __future__ import annotations

from pathlib import Path


BOOTSTRAP_CDN_CSS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
BOOTSTRAP_CDN_JS = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"


def register_bootstrap_theme(
    use_cdn: bool = True,
    local_css: str = "",
    local_js: str = "",
    custom_css: list[str] | None = None,
) -> dict[str, Any]:
    """Register a Bootstrap theme in the MikiUI theme registry.

    Parameters
    ----------
    use_cdn:
        Load Bootstrap from jsDelivr CDN.
    local_css:
        Path to local ``bootstrap.min.css`` (used when ``use_cdn`` is ``False``).
    local_js:
        Path or URL to Bootstrap JS bundle.
    custom_css:
        Extra CSS file paths to include.

    Returns
    -------
    dict
        The registered theme dict.
    """
    from ..themes import Theme, register_theme

    theme = Theme(
        name="bootstrap",
        source="builtin-framework",
        framework="bootstrap",
        cdn_url=BOOTSTRAP_CDN_CSS if use_cdn else None,
        js_url=BOOTSTRAP_CDN_JS if use_cdn else (local_js or None),
        css_path=local_css if not use_cdn else None,
        extra_classes=[],
    )
    register_theme(theme)
    return theme.to_dict()


def runtime_html(
    use_cdn: bool = True,
    local_css: str = "",
    local_js: str = "",
    custom_css: list[str] | None = None,
) -> str:
    """Return the ``<link>`` / ``<script>`` HTML for Bootstrap mode."""
    parts: list[str] = []
    if use_cdn:
        parts.append(f'<link rel="stylesheet" href="{BOOTSTRAP_CDN_CSS}">')
        parts.append(f'<script src="{BOOTSTRAP_CDN_JS}"></script>')
    else:
        if local_css:
            parts.append(f'<link rel="stylesheet" href="{local_css}">')
        if local_js:
            parts.append(f'<script src="{local_js}"></script>')
    for css in list(custom_css or []):
        parts.append(f'<link rel="stylesheet" href="{css}">')
    return "\n    ".join(parts)


def validate_bootstrap_paths(config: "BootstrapConfig", project_dir: str | Path = ".") -> list[str]:
    """Validate all file paths in a :class:`BootstrapConfig`.

    Returns a list of warning strings (empty list if all paths are valid).

    Parameters
    ----------
    config:
        BootstrapConfig to validate.
    project_dir:
        Project root for resolving relative paths.

    Returns
    -------
    list[str]
        Human-readable warnings for missing or inaccessible files.
    """
    warnings: list[str] = []
    project_dir = Path(project_dir).resolve()

    if not config.use_cdn:
        if config.local_css_path:
            resolved = (project_dir / config.local_css_path).resolve()
            if not resolved.is_file():
                warnings.append(
                    f"Bootstrap CSS not found at: {resolved}"
                )
        if config.local_js_path and not config.local_js_path.startswith("http"):
            resolved = (project_dir / config.local_js_path).resolve()
            if not resolved.is_file():
                warnings.append(
                    f"Bootstrap JS not found at: {resolved}"
                )

    for css_path in config.custom_css_paths:
        resolved = (project_dir / css_path).resolve()
        if not resolved.is_file():
            warnings.append(f"Custom CSS file not found: {resolved}")

    return warnings


def css_files_to_bundle(config: "BootstrapConfig", project_dir: str | Path = ".") -> list[str]:
    """Return the list of local CSS file paths to bundle in production.

    CDN files are skipped (they are fetched at runtime).

    Parameters
    ----------
    config:
        BootstrapConfig to inspect.
    project_dir:
        Project root for resolving relative paths.

    Returns
    -------
    list[str]
        Absolute paths to local CSS files.
    """
    project_dir = Path(project_dir).resolve()
    files: list[str] = []

    if not config.use_cdn and config.local_css_path:
        resolved = (project_dir / config.local_css_path).resolve()
        if resolved.is_file():
            files.append(str(resolved))

    for css_path in config.custom_css_paths:
        resolved = (project_dir / css_path).resolve()
        if resolved.is_file():
            files.append(str(resolved))

    return files


__all__ = [
    "BOOTSTRAP_CDN_CSS",
    "BOOTSTRAP_CDN_JS",
    "register_bootstrap_theme",
    "runtime_html",
    "validate_bootstrap_paths",
    "css_files_to_bundle",
]
