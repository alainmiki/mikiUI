"""MikiUI styling system.

Public surface:

* :class:`StylingSystem` — orchestrates framework detection, setup, and runtime
  CSS injection for **Tailwind**, **Bootstrap**, or **plain CSS**.
* :func:`detect_node` — check whether Node.js / npm are on PATH.
* :func:`write_tailwind_config` / :func:`setup_bootstrap` /
  :func:`setup_plain_css` — per-framework setup helpers.
* :func:`get_runtime_css` — return the correct ``<link>`` / ``<style>`` tags
  for the current framework and mode (dev vs. prod).
"""

from __future__ import annotations

from .bootstrap import (
    css_files_to_bundle,
    validate_bootstrap_paths,
)
from .bootstrap import (
    register_bootstrap_theme as setup_bootstrap,
)
from .bootstrap import (
    runtime_html as bootstrap_runtime_html,
)
from .plain_css import (
    css_files_to_bundle as plain_css_files_to_bundle,
)
from .plain_css import (
    runtime_html as plain_runtime_html,
)
from .plain_css import (
    setup_plain_css,
    validate_plain_css_paths,
)
from .runtime import css_head_block, get_runtime_css
from .system import (
    BootstrapConfig,
    Framework,
    NodeCheckResult,
    PlainCssConfig,
    StylingMode,
    StylingSystem,
    detect_node,
    normalize_framework,
    require_node,
)
from .tailwind import (
    daisyui_bridge,
    install_deps,
    npm_dependencies,
    write_config,
    write_postcss_config,
)

__all__ = [
    "Framework",
    "StylingMode",
    "NodeCheckResult",
    "StylingSystem",
    "BootstrapConfig",
    "PlainCssConfig",
    "detect_node",
    "normalize_framework",
    "require_node",
    "npm_dependencies",
    "write_config",
    "write_postcss_config",
    "install_deps",
    "daisyui_bridge",
    "setup_bootstrap",
    "validate_bootstrap_paths",
    "bootstrap_runtime_html",
    "css_files_to_bundle",
    "setup_plain_css",
    "validate_plain_css_paths",
    "plain_runtime_html",
    "plain_css_files_to_bundle",
    "get_runtime_css",
    "css_head_block",
]
