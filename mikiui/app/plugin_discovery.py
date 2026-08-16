"""Plugin discovery and auto-loading for MikiUI.

Scans directories and entry points to discover plugins. Supports:

1. **Directory scanning**: Loads modules from ``mikiui_app_plugins/`` and
   user-specified plugin directories.
2. **Entry points**: Discovers plugins registered via ``mikiui.plugins``
   entry points in ``pyproject.toml`` or ``setup.py``.
3. **Plugin metadata**: Reads plugin metadata (name, version, description,
   dependencies) from module attributes or package metadata.

Usage:
    from mikiui.app.plugin_discovery import discover_plugins, load_plugin

    # Discover all built-in plugins
    plugins = discover_plugins()

    # Load a specific plugin module
    plugin_cls = load_plugin("mikiui_app_plugins.notifications.NotificationPlugin")
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Metadata for a discovered plugin.

    Attributes:
        name: Plugin name.
        module_path: Full module path (e.g. ``"mikiui_app_plugins.api.APIPlugin"``).
        class_name: Plugin class name.
        version: Plugin version (from module or package metadata).
        description: Plugin description.
        dependencies: List of plugin names this plugin depends on.
        source: Where the plugin was discovered from.
    """

    name: str
    module_path: str
    class_name: str
    version: str = "0.0.0"
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    source: str = "unknown"


def _get_module_metadata(module: Any) -> PluginMetadata:
    """Extract plugin metadata from a module."""
    name = getattr(module, "__name__", "").split(".")[-1]
    metadata = PluginMetadata(
        name=getattr(module, "PLUGIN_NAME", name),
        module_path=getattr(module, "__name__", ""),
        class_name="",
        version=getattr(module, "__version__", "0.0.0"),
        description=getattr(module, "__doc__", "") or "",
        dependencies=getattr(module, "depends_on", []),
        source="module",
    )
    # Look for Plugin subclasses in the module
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (
            isinstance(attr, type)
            and attr_name != "Plugin"
            and hasattr(attr, "name")
            and attr_name != "Plugin"
        ):
            try:
                from mikiui.app.plugins import Plugin as _BasePlugin

                if issubclass(attr, _BasePlugin):
                    metadata.class_name = attr_name
                    metadata.name = getattr(attr, "name", attr_name)
                    metadata.dependencies = list(getattr(attr, "depends_on", []))
                    break
            except ImportError:
                pass
    return metadata


def discover_from_directory(directory: str | Path) -> list[PluginMetadata]:
    """Scan a directory for Python plugin modules.

    Parameters
    ----------
    directory:
        Path to scan for plugin modules.

    Returns
    -------
    list[PluginMetadata]
        Discovered plugin metadata.
    """
    directory = Path(directory)
    if not directory.is_dir():
        return []
    discovered = []
    for filepath in sorted(directory.rglob("*.py")):
        if filepath.name.startswith("_") or filepath.name == "__init__.py":
            continue
        module_name = filepath.stem
        # Try to import the module
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        if spec is None or spec.loader is None:
            continue
        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            metadata = _get_module_metadata(module)
            metadata.source = f"directory:{directory}"
            discovered.append(metadata)
        except Exception:
            logger.debug("Failed to load plugin module %s: %s", filepath, exc_info=True)
    return discovered


def discover_from_entry_points() -> list[PluginMetadata]:
    """Discover plugins registered via ``mikiui.plugins`` entry points.

    Returns
    -------
    list[PluginMetadata]
        Discovered plugin metadata.
    """
    discovered = []
    try:
        from importlib.metadata import entry_points

        eps = entry_points()
        if hasattr(eps, "select"):
            plugin_eps = eps.select(group="mikiui.plugins")
        else:
            plugin_eps = eps.get("mikiui.plugins", [])
        for ep in plugin_eps:
            try:
                cls = ep.load()
                metadata = PluginMetadata(
                    name=getattr(cls, "name", ep.name),
                    module_path=ep.value,
                    class_name=ep.attr,
                    version=getattr(cls, "__version__", "0.0.0"),
                    description=getattr(cls, "__doc__", "") or "",
                    dependencies=list(getattr(cls, "depends_on", [])),
                    source="entry_point",
                )
                discovered.append(metadata)
            except Exception:
                logger.debug(
                    "Failed to load entry point plugin %s: %s",
                    ep.name, exc_info=True,
                )
    except ImportError:
        logger.debug(
            "importlib.metadata not available; skipping entry point discovery."
        )
    return discovered


def discover_plugins(
    *,
    include_builtins: bool = True,
    plugin_dirs: list[str | Path] | None = None,
    include_entry_points: bool = True,
) -> list[PluginMetadata]:
    """Discover available MikiUI plugins.

    Parameters
    ----------
    include_builtins:
        If True, scan the built-in ``mikiui_app_plugins`` directory.
    plugin_dirs:
        Additional directories to scan for plugins.
    include_entry_points:
        If True, include plugins registered via entry points.

    Returns
    -------
    list[PluginMetadata]
        List of discovered plugin metadata, sorted by name.
    """
    discovered: list[PluginMetadata] = []

    if include_builtins:
        builtin_dir = (
            Path(__file__).resolve().parent.parent.parent / "mikiui_app_plugins"
        )
        discovered.extend(discover_from_directory(builtin_dir))

    for d in (plugin_dirs or []):
        discovered.extend(discover_from_directory(d))

    if include_entry_points:
        discovered.extend(discover_from_entry_points())

    # Deduplicate by module_path
    seen: set[str] = set()
    unique = []
    for meta in discovered:
        if meta.module_path not in seen:
            seen.add(meta.module_path)
            unique.append(meta)

    return sorted(unique, key=lambda m: m.name)


def load_plugin(module_path: str) -> type | None:
    """Load a plugin class from a module path.

    Parameters
    ----------
    module_path:
        Full module path, optionally with class name
        (e.g. ``"mikiui_app_plugins.api.APIPlugin"``).

    Returns
    -------
    type | None
        The plugin class, or None if not found.
    """
    if ":" in module_path:
        module_name, class_name = module_path.rsplit(":", 1)
    else:
        module_name = module_path
        class_name = None
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        logger.debug("Failed to import plugin module %s.", module_name, exc_info=True)
        return None
    if class_name:
        return getattr(module, class_name, None)
    # Find the first Plugin subclass
    from mikiui.app.plugins import Plugin as _BasePlugin

    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (
            isinstance(attr, type)
            and issubclass(attr, _BasePlugin)
            and attr is not _BasePlugin
        ):
            return attr
    return None


def auto_load(
    app: Any,
    *,
    include_builtins: bool = True,
    plugin_dirs: list[str | Path] | None = None,
    include_entry_points: bool = True,
) -> list[Any]:
    """Discover and register plugins on an app.

    Parameters
    ----------
    app:
        The MikiApp instance to register plugins on.
    include_builtins:
        If True, include built-in plugins.
    plugin_dirs:
        Additional directories to scan.
    include_entry_points:
        If True, include entry point plugins.

    Returns
    -------
    list[Any]
        List of instantiated and registered plugins.
    """
    discovered = discover_plugins(
        include_builtins=include_builtins,
        plugin_dirs=plugin_dirs,
        include_entry_points=include_entry_points,
    )
    registered = []
    for meta in discovered:
        if meta.class_name:
            cls = load_plugin(f"{meta.module_path}:{meta.class_name}")
            if cls:
                try:
                    plugin = cls()
                    app.use(plugin)
                    registered.append(plugin)
                except Exception:
                    logger.debug(
                        "Failed to instantiate plugin %s.",
                        meta.name, exc_info=True,
                    )
    return registered


__all__ = [
    "PluginMetadata",
    "discover_plugins",
    "discover_from_directory",
    "discover_from_entry_points",
    "load_plugin",
    "auto_load",
]
