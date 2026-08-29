"""Core StylingSystem class and Node.js detection.

This module is the single entry-point for the MikiUI styling lifecycle:

1. **Framework selection** — user picks Tailwind or plain CSS.
2. **Prerequisite checks** — Node.js detection for Tailwind; warn or abort.
3. **Setup** — write config files, install npm deps (Tailwind), or register
   plain CSS theme in the theme registry.
4. **Runtime injection** — return the correct ``<link>`` / ``<style>`` tags
   for the current mode (dev vs. prod).

Security note: no secrets (API keys, tokens, private keys) are read, stored,
or written by this module.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class Framework(StrEnum):
    TAILWIND = "tailwind"
    PLAIN = "plain"


def normalize_framework(value: str) -> tuple[str, bool]:
    """Normalize a framework string to (base_framework, daisyui_enabled).

    ``"daisyui"`` is treated as ``"tailwind"`` with DaisyUI enabled.
    """
    if value == "daisyui":
        return "tailwind", True
    return value, False


class StylingMode(StrEnum):
    DEV = "dev"
    PROD = "prod"


class NodeCheckResult:
    """Result of a Node.js / npm availability check."""

    def __init__(self, node_ok: bool, npm_ok: bool, node_version: str | None = None) -> None:
        self.node_ok = node_ok
        self.npm_ok = npm_ok
        self.node_version = node_version

    @property
    def available(self) -> bool:
        return self.node_ok and self.npm_ok

    def __bool__(self) -> bool:
        return self.available

    def __repr__(self) -> str:
        return (
            f"NodeCheckResult(node={self.node_ok}, npm={self.npm_ok}, "
            f"version={self.node_version!r})"
        )


# ---------------------------------------------------------------------------
# Node.js detection
# ---------------------------------------------------------------------------

def detect_node() -> NodeCheckResult:
    """Return a :class:`NodeCheckResult` describing the Node.js environment.

    Checks ``node`` and ``npm`` on PATH.  Does *not* modify the system.
    """
    node_path = shutil.which("node")
    npm_path = shutil.which("npm")
    node_version = None
    if node_path:
        try:
            result = subprocess.run(
                [node_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            node_version = result.stdout.strip() if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            pass
    return NodeCheckResult(
        node_ok=node_path is not None,
        npm_ok=npm_path is not None,
        node_version=node_version,
    )


def require_node() -> NodeCheckResult:
    """Like :func:`detect_node` but raises if Node.js is missing.

    Raises
    ------
    SystemExit
        If Node.js or npm is not installed, prints an actionable message
        and exits with code 1.
    """
    result = detect_node()
    if not result.available:
        print(
            "Node.js is required for Tailwind CSS.\n"
            "  Install it from https://nodejs.org/\n"
            "  Then run 'npm install' in your project directory.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return result


# ---------------------------------------------------------------------------
# Configuration dataclasses
# ---------------------------------------------------------------------------

@dataclass
class TailwindConfig:
    """Tailwind-specific styling configuration."""

    framework: Framework = Framework.TAILWIND
    daisyui: bool = False
    theme: str = "light"
    use_cdn: bool = False
    custom_css_paths: list[str] = field(default_factory=list)


@dataclass
class PlainCssConfig:
    """Plain-CSS (no framework) configuration."""

    framework: Framework = Framework.PLAIN
    mode: str = "cdn"
    custom_css_paths: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# StylingSystem
# ---------------------------------------------------------------------------

class StylingSystem:
    """High-level styling orchestrator.

    Tracks the current framework configuration and produces the correct
    runtime HTML for both dev and production environments.

    Parameters
    ----------
    project_dir:
        Root directory of the MikiUI project (where ``app.py`` lives).
    mode:
        ``StylingMode.DEV`` or ``StylingMode.PROD``.

    Examples
    --------
    >>> ss = StylingSystem(project_dir=".")
    >>> ss.auto_setup(framework="tailwind", daisyui=True)
    >>> html = ss.runtime_css()

    Or use the CLI-oriented constructor:

    >>> ss = StylingSystem.from_cli(framework="tailwind")
    """

    def __init__(
        self,
        project_dir: str | Path = ".",
        mode: StylingMode = StylingMode.DEV,
    ) -> None:
        self.project_dir = Path(project_dir).resolve()
        self.mode = mode
        self._framework: Framework | None = None
        self._tailwind: TailwindConfig | None = None
        self._plain: PlainCssConfig | None = None
        self._errors: list[str] = []

    @classmethod
    def from_cli(
        cls,
        framework: str = "tailwind",
        project_dir: str | Path = ".",
        **kwargs: Any,
    ) -> StylingSystem:
        """Create a StylingSystem from CLI-style arguments and run setup.

        This is the recommended constructor for CLI commands. It normalizes
        the framework string (e.g. ``"daisyui"`` → tailwind + DaisyUI),
        runs ``auto_setup``, and returns the ready-to-use instance.

        Parameters
        ----------
        framework:
            One of ``"tailwind"``, ``"plain"``, or
            ``"daisyui"``.
        project_dir:
            Project root directory.
        **kwargs:
            Extra keyword arguments forwarded to :meth:`auto_setup`.

        Returns
        -------
        StylingSystem
            Configured and ready-to-use instance.
        """
        ss = cls(project_dir=project_dir)
        ss.auto_setup(framework=framework, **kwargs)
        return ss

    @classmethod
    def detect(cls, project_dir: str | Path = ".") -> StylingSystem:
        """Auto-detect the styling framework from project files.

        Looks for ``tailwind.config.js``, ``package.json`` with Tailwind
        deps, or plain CSS references to guess the framework.

        Parameters
        ----------
        project_dir:
            Project root directory to inspect.

        Returns
        -------
        StylingSystem
            Instance with the detected framework already set up.
        """
        ss = cls(project_dir=project_dir)
        detected = ss._detect_framework()
        ss.auto_setup(framework=detected)
        return ss

    def _detect_framework(self) -> str:
        """Inspect project files to guess the styling framework."""
        project_dir = self.project_dir

        if (project_dir / "tailwind.config.js").is_file():
            return "tailwind"
        if (project_dir / "package.json").is_file():
            try:
                import json
                pkg = json.loads(
                    (project_dir / "package.json").read_text(encoding="utf-8")
                )
                all_deps = {
                    **pkg.get("dependencies", {}),
                    **pkg.get("devDependencies", {}),
                }
                if "tailwindcss" in all_deps or "daisyui" in all_deps:
                    return "tailwind"
            except (json.JSONDecodeError, OSError):
                pass
        return "plain"

    # -- properties -----------------------------------------------------------

    @property
    def framework(self) -> Framework | None:
        return self._framework

    @framework.setter
    def framework(self, value: Framework) -> None:
        self._framework = value

    @property
    def tailwind_config(self) -> TailwindConfig | None:
        return self._tailwind

    @property
    def plain_config(self) -> PlainCssConfig | None:
        return self._plain

    @property
    def errors(self) -> list[str]:
        return list(self._errors)

    # -- public API -----------------------------------------------------------
    def auto_setup(
        self,
        framework: str = "tailwind",
        daisyui: bool = False,
        theme: str = "light",
        custom_css: list[str] | None = None,
    ) -> dict[str, Any]:
        """Detect prerequisites and set up the selected framework.

        Parameters
        ----------
        framework:
            One of ``"tailwind"``, ``"plain"``, or ``"daisyui"``.
        daisyui:
            Enable DaisyUI (Tailwind only, also implied by ``"daisyui"`` framework).
        theme:
            Active color theme name.
        custom_css:
            Additional CSS file paths (all frameworks).

        Returns
        -------
        dict
            Report with keys: ``framework``, ``status``, ``warnings``,
            ``instructions`` (user-facing next steps).
        """
        custom_css = custom_css or []
        report: dict[str, Any] = {
            "framework": framework,
            "status": "ok",
            "warnings": [],
            "instructions": [],
        }

        base_fw, daisyui_enabled = normalize_framework(framework)
        try:
            fw = Framework(base_fw)
        except ValueError:
            valid = ", ".join(f.value for f in Framework)
            raise ValueError(
                f"Unknown framework {framework!r}. Choose from: {valid}"
            )

        self._framework = fw

        if fw == Framework.TAILWIND:
            self._setup_tailwind(
                daisyui=daisyui or daisyui_enabled,
                theme=theme,
                custom_css=custom_css,
                report=report,
            )
        else:
            self._plain = PlainCssConfig(custom_css_paths=list(custom_css))

        return report

    def runtime_css(self, mode: StylingMode | None = None) -> str:
        """Return the ``<link>`` / ``<style>`` HTML for the current framework.

        Parameters
        ----------
        mode:
            Override the runtime mode (``StylingMode.DEV`` or ``PROD``).
            Defaults to :attr:`self.mode`.

        Returns
        -------
        str
            HTML string suitable for injection into ``<head>``.
        """
        effective_mode = mode or self.mode

        if self._framework == Framework.TAILWIND:
            return _tailwind_runtime_html(
                config=self._tailwind,
                mode=effective_mode,
                project_dir=self.project_dir,
            )
        return _plain_runtime_html(config=self._plain, project_dir=self.project_dir)

    def get_css_files(self) -> list[str]:
        """Return ordered list of CSS file paths that should be bundled."""
        files: list[str] = []
        if self._framework == Framework.TAILWIND:
            files.extend(self._collect_tailwind_css_files())
        if self._plain:
            files.extend(self._plain.custom_css_paths)
        return files

    # -- private: per-framework setup -----------------------------------------

    def _setup_tailwind(
        self,
        daisyui: bool,
        theme: str,
        custom_css: list[str],
        report: dict[str, Any],
    ) -> None:
        from ..styling.tailwind import write_config, write_postcss_config

        node = detect_node()
        if not node.available:
            report["status"] = "node_required"
            report["instructions"] = [
                "Node.js is required to use Tailwind CSS.",
                "Install Node.js from https://nodejs.org/",
                "After installing, run 'npm install' in your project directory.",
                "Then run 'mikiui dev' or 'mikiui build' as usual.",
            ]
            report["warnings"].append(
                f"Node.js not found (node={node.node_ok}, npm={node.npm_ok}). "
                "Tailwind JIT build is unavailable."
            )
            self._tailwind = TailwindConfig(
                daisyui=daisyui,
                theme=theme,
                use_cdn=True,
                custom_css_paths=list(custom_css),
            )
            return

        self._tailwind = TailwindConfig(
            daisyui=daisyui,
            theme=theme,
            use_cdn=False,
            custom_css_paths=list(custom_css),
        )

        write_config(
            str(self.project_dir / "tailwind.config.js"),
            theme=theme,
            daisyui=daisyui,
        )
        write_postcss_config(str(self.project_dir / "postcss.config.js"))

        self._register_tailwind_theme(theme=theme, daisyui=daisyui)

        report["instructions"] = [
            "Tailwind CSS configured successfully.",
            f"  DaisyUI: {'enabled' if daisyui else 'disabled'}",
            f"  Theme: {theme}",
            "Run 'npm install' to install dependencies (if not already done).",
            "Then run 'mikiui dev' to start developing.",
        ]

    def _register_tailwind_theme(self, theme: str, daisyui: bool) -> None:
        from ..themes import Theme, register_theme

        tailwind_css = self.project_dir / "mikiui" / "runtime" / "themes" / "tailwind.css"
        built_css = self.project_dir / "_miki" / "runtime" / "themes" / "tailwind.css"
        css_path: str | None = None
        if built_css.is_file():
            css_path = str(built_css)
        elif tailwind_css.is_file():
            css_path = str(tailwind_css)

        if css_path is None:
            return

        theme_obj = Theme(
            name="tailwind",
            source="styling-system",
            framework="tailwind",
            css_path=css_path,
            tailwind_config={"daisyui": daisyui},
            color_theme=theme,
        )
        register_theme(theme_obj)

    # -- private: CSS file collection -----------------------------------------

    def _collect_tailwind_css_files(self) -> list[str]:
        files: list[str] = []
        tailwind_css = self.project_dir / "mikiui" / "runtime" / "themes" / "tailwind.css"
        if tailwind_css.is_file():
            files.append(str(tailwind_css))
        built_css = self.project_dir / "_miki" / "runtime" / "themes" / "tailwind.css"
        if built_css.is_file():
            files.append(str(built_css))
        if self._tailwind:
            files.extend(self._tailwind.custom_css_paths)
        return files


# ---------------------------------------------------------------------------
# Helpers: runtime HTML generation
# ---------------------------------------------------------------------------

def _tailwind_runtime_html(
    config: TailwindConfig | None,
    mode: StylingMode,
    project_dir: Path,
) -> str:
    """Generate the <link> tags for Tailwind mode."""
    if config is None:
        return ""

    parts: list[str] = []

    if config.use_cdn:
        parts.append('<script src="https://cdn.tailwindcss.com"></script>')
        if config.daisyui:
            daisyui_cdn = "https://cdn.jsdelivr.net/npm/daisyui@5/dist/daisyui.css"
            parts.append(f'<link rel="stylesheet" href="{daisyui_cdn}">')
    else:
        tailwind_css = project_dir / "mikiui" / "runtime" / "themes" / "tailwind.css"
        if tailwind_css.is_file():
            parts.append('<link rel="stylesheet" href="/_miki/runtime/themes/tailwind.css">')
        built_css = project_dir / "_miki" / "runtime" / "themes" / "tailwind.css"
        if built_css.is_file() and not tailwind_css.is_file():
            parts.append('<link rel="stylesheet" href="/_miki/runtime/themes/tailwind.css">')

    for css_path in config.custom_css_paths:
        parts.append(f'<link rel="stylesheet" href="{css_path}">')

    return "\n    ".join(parts)


def _plain_runtime_html(
    config: PlainCssConfig | None,
    project_dir: Path,
) -> str:
    """Generate the <link> tags for plain-CSS mode."""
    if config is None:
        return ""
    parts = [f'<link rel="stylesheet" href="{p}">' for p in config.custom_css_paths]
    return "\n    ".join(parts)


# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------

__all__ = [
    "Framework",
    "StylingMode",
    "StylingSystem",
    "NodeCheckResult",
    "detect_node",
    "require_node",
    "TailwindConfig",
    "PlainCssConfig",
]
