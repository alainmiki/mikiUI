"""Plain-CSS helpers for the MikiUI styling system.

Used when the user opts out of Tailwind.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .system import PlainCssConfig


def register_plain_theme(custom_css: list[str] | None = None) -> dict[str, Any]:
    """Register a plain-CSS theme in the MikiUI theme registry.

    Parameters
    ----------
    custom_css:
        Extra CSS file paths to include.

    Returns
    -------
    dict
        The registered theme dict.
    """
    from ..themes import Theme, register_theme

    theme = Theme(
        name="light",
        source="builtin-framework",
        framework="css",
        extra_classes=[],
    )
    register_theme(theme)
    return theme.to_dict()


def setup_plain_css(
    custom_css: list[str] | None = None,
    project_dir: str | Path = ".",
) -> PlainCssConfig:
    """Create and validate a :class:`PlainCssConfig`.

    Parameters
    ----------
    custom_css:
        CSS file paths to include (relative to *project_dir* or absolute).
    project_dir:
        Project root directory used to resolve relative paths.

    Returns
    -------
    PlainCssConfig
        The validated configuration.

    Raises
    ------
    FileNotFoundError
        If any of the *custom_css* paths do not point to an existing file.
    """
    from ..system import PlainCssConfig

    paths = list(custom_css or [])
    project_dir = Path(project_dir).resolve()

    for p in paths:
        resolved = (project_dir / p).resolve()
        if not resolved.is_file():
            raise FileNotFoundError(
                f"Custom CSS file not found: {resolved} (from path: {p!r})"
            )

    return PlainCssConfig(custom_css_paths=paths)  # type: ignore[no-any-return]


def runtime_html(custom_css: list[str] | None = None) -> str:
    """Return the ``<link>`` HTML for plain-CSS mode."""
    parts = [f'<link rel="stylesheet" href="{p}">' for p in list(custom_css or [])]
    return "\n    ".join(parts)


def runtime_css(config: PlainCssConfig | None, project_dir: Path | None = None) -> str:
    """Return ``<link>`` tags for plain-CSS mode.

    Parameters
    ----------
    config:
        PlainCssConfig (or ``None``).
    project_dir:
        Project root (currently unused, kept for API symmetry).

    Returns
    -------
    str
        HTML string for ``<head>`` injection.
    """
    if config is None:
        return ""
    parts = [f'<link rel="stylesheet" href="{p}">' for p in config.custom_css_paths]
    return "\n    ".join(parts)


def css_files_to_bundle(
    config: PlainCssConfig,
    project_dir: str | Path = ".",
) -> list[str]:
    """Return absolute paths of all CSS files to bundle for production.

    Parameters
    ----------
    config:
        PlainCssConfig to inspect.
    project_dir:
        Project root for resolving relative paths.

    Returns
    -------
    list[str]
        Absolute paths to existing CSS files.
    """
    project_dir = Path(project_dir).resolve()
    files: list[str] = []

    for css_path in config.custom_css_paths:
        resolved = (project_dir / css_path).resolve()
        if resolved.is_file():
            files.append(str(resolved))

    return files


def validate_plain_css_paths(
    config: PlainCssConfig,
    project_dir: str | Path = ".",
) -> list[str]:
    """Validate all CSS paths in a :class:`PlainCssConfig`.

    Parameters
    ----------
    config:
        PlainCssConfig to validate.
    project_dir:
        Project root for resolving relative paths.

    Returns
    -------
    list[str]
        Human-readable warnings for missing files (empty = all OK).
    """
    warnings: list[str] = []
    project_dir = Path(project_dir).resolve()

    for css_path in config.custom_css_paths:
        resolved = (project_dir / css_path).resolve()
        if not resolved.is_file():
            warnings.append(f"Custom CSS file not found: {resolved}")

    return warnings


__all__ = [
    "register_plain_theme",
    "setup_plain_css",
    "runtime_html",
    "runtime_css",
    "css_files_to_bundle",
    "validate_plain_css_paths",
]
