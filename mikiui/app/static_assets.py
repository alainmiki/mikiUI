"""Static asset registry for MikiUI components, widgets, and plugins.

Discovers ``static/`` directories inside component packages, widget packages,
and plugin asset paths.  The server mounts each discovered directory under
``/_miki/`` so assets are served with proper caching and no inline bloat.

Security
--------
* Only directories explicitly discovered during startup are mounted.
* Paths are validated to prevent directory traversal.
* No user-controlled paths are served.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

# Package roots that may contain ``static/`` subdirectories.
_PACKAGE_ROOTS: list[str] = []

# Mapping of URL mount path -> absolute filesystem path.
# Example: {
#   "/_miki/components/splitview/static": "/abs/path/to/mikiui/components/splitview/static",
#   "/_miki/widgets/dockable_panel/static": "/abs/path/to/mikiui/widgets/dockable_panel/static",
# }
_ASSET_MOUNTS: dict[str, str] = {}

# Reverse mapping: absolute filesystem path -> URL mount path.
_ABS_TO_URL: dict[str, str] = {}

# Plugin-registered mounts preserved across discover() calls.
_PLUGIN_MOUNTS: dict[str, str] = {}
_PLUGIN_ABS_TO_URL: dict[str, str] = {}


def register_package_root(abs_path: str) -> None:
    """Register a package root directory for static asset discovery.

    Parameters
    ----------
    abs_path:
        Absolute path to a package directory (e.g. ``mikiui/components``,
        ``mikiui/widgets``, or a plugin's root directory).
    """
    abs_path = os.path.abspath(abs_path)
    if abs_path not in _PACKAGE_ROOTS:
        _PACKAGE_ROOTS.append(abs_path)
        logger.debug("Registered static asset root: %s", abs_path)


def discover() -> dict[str, str]:
    """Scan all registered package roots for ``static/`` directories.

    Plugin-registered mounts are preserved across calls.

    Returns
    -------
    dict[str, str]
        Mapping of URL mount path -> absolute filesystem path.
    """
    _ASSET_MOUNTS.clear()
    _ABS_TO_URL.clear()

    for root in _PACKAGE_ROOTS:
        _scan_root(root)

    # Merge plugin-registered mounts back in
    _ASSET_MOUNTS.update(_PLUGIN_MOUNTS)
    _ABS_TO_URL.update(_PLUGIN_ABS_TO_URL)

    return dict(_ASSET_MOUNTS)


def _scan_root(root: str) -> None:
    """Scan a single package root for ``static/`` directories."""
    if not os.path.isdir(root):
        return

    try:
        entries = os.listdir(root)
    except OSError:
        return

    for entry in entries:
        entry_path = os.path.join(root, entry)
        static_dir = os.path.join(entry_path, "static")
        if os.path.isdir(static_dir):
            # Build URL: /_miki/<root_basename>/<package_name>/static
            root_name = os.path.basename(root.rstrip(os.sep))
            url_path = f"/_miki/{root_name}/{entry}/static"
            abs_path = os.path.abspath(static_dir)

            if abs_path not in _ABS_TO_URL:
                _ASSET_MOUNTS[url_path] = abs_path
                _ABS_TO_URL[abs_path] = url_path
                logger.debug(
                    "Discovered static assets: %s -> %s", url_path, abs_path
                )


def get_asset_url(package_type: str, package_name: str, filename: str) -> str:
    """Build the URL for a static asset.

    Parameters
    ----------
    package_type:
        One of ``"components"``, ``"widgets"``, or ``"plugins"``.
    package_name:
        The package/plugin name (e.g. ``"splitview"``).
    filename:
        The asset filename (e.g. ``"splitview.css"``).

    Returns
    -------
    str
        URL path to the asset, e.g.
        ``/_miki/components/splitview/static/splitview.css``.
    """
    safe_pkg = package_name.strip("/")
    safe_file = filename.strip("/")
    return f"/_miki/{package_type}/{safe_pkg}/static/{safe_file}"


def get_asset_mounts() -> dict[str, str]:
    """Return all discovered asset mounts (URL path -> filesystem path)."""
    return dict(_ASSET_MOUNTS)


def get_asset_dir(package_type: str, package_name: str) -> str | None:
    """Return the absolute filesystem path for a package's static directory.

    Parameters
    ----------
    package_type:
        One of ``"components"``, ``"widgets"``, or ``"plugins"``.
    package_name:
        The package/plugin name.

    Returns
    -------
    str | None
        Absolute path to the static directory, or ``None`` if not found.
    """
    url_path = f"/_miki/{package_type}/{package_name}/static"
    return _ASSET_MOUNTS.get(url_path)


def resolve_static_path(url_path: str) -> str | None:
    """Resolve a URL path to an absolute filesystem path.

    Parameters
    ----------
    url_path:
        URL path like ``/_miki/components/splitview/static/splitview.css``.

    Returns
    -------
    str | None
        Absolute filesystem path, or ``None`` if the path is not within a
        registered static directory.
    """
    # Find the longest matching mount prefix
    best_match: str | None = None
    best_len = 0
    for mount_url, abs_path in _ASSET_MOUNTS.items():
        if url_path.startswith(mount_url) and len(mount_url) > best_len:
            best_match = mount_url
            best_len = len(mount_url)

    if best_match is None:
        return None

    relative = url_path[best_len:].lstrip("/")
    resolved = os.path.normpath(os.path.join(abs_path, relative))
    abs_path = _ASSET_MOUNTS[best_match]

    # Security: ensure resolved path is within the static directory
    if not resolved.startswith(abs_path + os.sep) and resolved != abs_path:
        return None

    return resolved


def init_defaults() -> None:
    """Register the default package roots for discovery.

    Call this early in server startup, before :func:`discover`.
    """
    _register_default_roots()


def _register_default_roots() -> None:
    """Register built-in package roots."""
    try:
        import mikiui

        base_dir = os.path.dirname(os.path.abspath(mikiui.__file__))

        register_package_root(os.path.join(base_dir, "components"))
        register_package_root(os.path.join(base_dir, "widgets"))
        register_package_root(os.path.join(base_dir, "plugins"))
        register_package_root(os.path.join(base_dir, "runtime", "themes"))
    except ImportError:
        pass


def register_plugin_assets(plugin_name: str, asset_paths: list[str]) -> None:
    """Register static asset directories from a plugin.

    Parameters
    ----------
    plugin_name:
        The plugin name (used in the URL path).
    asset_paths:
        List of absolute paths to static asset directories provided by the
        plugin via :meth:`Plugin.assets`.
    """
    for path in asset_paths:
        abs_path = os.path.abspath(path)
        if not os.path.isdir(abs_path):
            logger.warning("Plugin %r asset path does not exist: %s", plugin_name, abs_path)
            continue

        # Deduplicate by absolute path so the same directory isn't mounted twice
        if abs_path in _PLUGIN_ABS_TO_URL:
            logger.debug(
                "Plugin %r asset path already registered: %s", plugin_name, abs_path
            )
            continue

        url_path = f"/_miki/plugins/{plugin_name}/static"
        _PLUGIN_MOUNTS[url_path] = abs_path
        _PLUGIN_ABS_TO_URL[abs_path] = url_path
        _ASSET_MOUNTS[url_path] = abs_path
        _ABS_TO_URL[abs_path] = url_path
        logger.debug(
            "Registered plugin static assets: %s -> %s", url_path, abs_path
        )


__all__ = [
    "register_package_root",
    "discover",
    "get_asset_url",
    "get_asset_mounts",
    "get_asset_dir",
    "resolve_static_path",
    "init_defaults",
    "register_plugin_assets",
]
