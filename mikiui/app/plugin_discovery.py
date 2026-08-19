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
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .plugin_security import (
    PluginManifest,
    PluginSecurityConfig,
    PluginSecurityViolation,
    PluginValidator,
    load_manifest,
)

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

                if issubclass(attr, _BasePlugin) and attr.__module__ == module.__name__:
                    metadata.class_name = attr_name
                    metadata.name = getattr(attr, "name", attr_name)
                    metadata.dependencies = list(getattr(attr, "depends_on", []))
                    break
            except ImportError:
                pass
    return metadata


def _module_relpath(base: Path, filepath: Path) -> str:
    """Return the dotted package-relative module path for *filepath* under *base*.

    Example: ``base=.../mikiui_app_plugins``, ``filepath=.../mikiui_app_plugins/notifications.py``
    -> ``"notifications"``.  For a nested module ``.../mikiui_app_plugins/sub/mod.py``
    -> ``"sub.mod"``.
    """
    rel = filepath.relative_to(base)
    parts = list(rel.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]  # strip .py
    return ".".join(parts)


def _import_module_rel(base: Path, filepath: Path) -> Any | None:
    """Import *filepath* (located under *base*) using a package-qualified name.

    The directory *base* is treated as a package root when it contains an
    ``__init__.py``; otherwise we fall back to loading the file by path while
    still registering the resulting module in ``sys.modules`` so that
    ``dataclasses._is_type`` and relative imports inside the module work.
    """
    import sys

    is_package = (base / "__init__.py").is_file()
    if is_package:
        # Resolve the package's dotted name by walking up package dirs.
        pkg_parts: list[str] = []
        cur: Path | None = base
        while cur is not None and (cur / "__init__.py").is_file():
            pkg_parts.insert(0, cur.name)
            parent = cur.parent
            # Stop at the repo root / first dir without __init__.py
            if parent is None or not (parent / "__init__.py").is_file():
                break
            cur = parent
        # Verify the top-level package is importable.
        top_pkg = pkg_parts[0] if pkg_parts else None
        if top_pkg is None:
            return None
        try:
            importlib.import_module(top_pkg)
        except Exception:
            # The package itself isn't importable; fall through to path load.
            is_package = False

    if is_package:
        dotted = ".".join(pkg_parts + _module_relpath(base, filepath).split("."))
        return importlib.import_module(dotted)

    # Fallback for standalone plugin dirs without __init__.py.
    dotted = _module_relpath(base, filepath)
    # Sanitize to a valid Python identifier (replace hyphens, etc.).
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", dotted)
    # Ensure the parent directory is on sys.path so the module's own imports
    # (e.g. `from mikiui import ...`) resolve from the project root, and so
    # that a later importlib.import_module(sanitized) can find it.
    parent = str(filepath.parent)
    if parent not in sys.path:
        sys.path.insert(0, parent)
    try:
        spec = importlib.util.spec_from_file_location(sanitized, filepath)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[sanitized] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(sanitized, None)
            raise
        return module
    finally:
        sys.path.remove(parent)


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
        try:
            module = _import_module_rel(directory, filepath)
        except Exception:
            logger.debug(
                "Failed to load plugin module %s: %s", filepath, exc_info=True
            )
            continue
        if module is None:
            continue
        metadata = _get_module_metadata(module)
        metadata.source = f"directory:{directory}"
        discovered.append(metadata)
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
        metas = discover_from_directory(builtin_dir)
        for meta in metas:
            meta.source = "builtin"
        discovered.extend(metas)

    for d in (plugin_dirs or []):
        metas = discover_from_directory(d)
        for meta in metas:
            if meta.source.startswith("directory:"):
                meta.source = "directory"
        discovered.extend(metas)

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


def _topological_sort(metas: list[PluginMetadata]) -> list[PluginMetadata]:
    """Order discovered plugins so each appears after its ``depends_on`` deps.

    Plugins whose dependencies cannot be satisfied are kept (the app's
    ``use()`` will raise a clear error) but placed last so that any resolvable
    plugins register first.  This is best-effort: missing deps still surface
    as a RuntimeError at registration time.
    """
    by_name: dict[str, PluginMetadata] = {m.name: m for m in metas}
    seen: set[str] = set()
    order: list[PluginMetadata] = []
    visiting: set[str] = set()

    def visit(meta: PluginMetadata) -> None:
        if meta.name in seen:
            return
        if meta.name in visiting:
            # Cycle: emit a warning and continue to avoid infinite loop.
            logger.warning(
                "Circular plugin dependency detected at %r; registering out of order.",
                meta.name,
            )
            seen.add(meta.name)
            return
        visiting.add(meta.name)
        for dep in meta.dependencies:
            if dep in by_name:
                visit(by_name[dep])
        visiting.discard(meta.name)
        seen.add(meta.name)
        order.append(meta)

    for meta in metas:
        visit(meta)
    return order


def auto_load(
    app: Any,
    *,
    include_builtins: bool = True,
    plugin_dirs: list[str | Path] | None = None,
    include_entry_points: bool = True,
    security_config: PluginSecurityConfig | None = None,
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
    security_config:
        Optional security policy.  When omitted the app's own
        ``_plugin_validator`` is used if available; otherwise the default
        :class:`PluginSecurityConfig` is applied.

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
    # Register in dependency order so ``depends_on`` is satisfied.
    ordered = _topological_sort(discovered)

    # Resolve the validator: prefer the app's own policy unless an explicit
    # security_config is passed for this auto_load call.
    if security_config is not None:
        validator = PluginValidator(security_config)
    else:
        validator = getattr(app, "_plugin_validator", None) or PluginValidator()

    # Enforce allow_untrusted: filter out plugins from untrusted sources.
    if not validator.config.allow_untrusted:
        trusted_sources = {"builtin", "entry_point"}
        filtered = []
        for meta in ordered:
            if meta.source in trusted_sources:
                filtered.append(meta)
            else:
                logger.warning(
                    "Plugin %r from untrusted source %r is skipped (allow_untrusted=False).",
                    meta.name,
                    meta.source,
                )
        ordered = filtered

    registered = []
    seen_classes: set[type] = set()

    for meta in ordered:
        if not meta.class_name:
            continue
        cls = load_plugin(f"{meta.module_path}:{meta.class_name}")
        if cls is None or cls in seen_classes:
            continue
        seen_classes.add(cls)
        try:
            plugin = cls()
            # Validate before registering.
            manifest = _load_manifest_for_class(plugin)
            source_code = _resolve_source_for_class(plugin)
            validator.validate_plugin(plugin, manifest=manifest, source_code=source_code)
            app.use(plugin)
            registered.append(plugin)
        except PluginSecurityViolation:
            logger.warning(
                "Plugin %r failed security validation; skipping.", meta.name
            )
        except Exception:
            logger.debug(
                "Failed to instantiate plugin %s.",
                meta.name,
                exc_info=True,
            )
    return registered


def _load_manifest_for_class(plugin: Any) -> PluginManifest | None:
    """Load a manifest for a plugin class, trying module attrs then plugin.json."""
    module = getattr(plugin, "__module__", None)
    if not module:
        return None
    try:
        import importlib

        mod = importlib.import_module(module)
        return load_manifest(mod)
    except ImportError:
        return None


def _resolve_source_for_class(plugin: Any) -> str | None:
    """Resolve raw source code for a plugin class by module name."""
    module = getattr(plugin, "__module__", None)
    if not module:
        return None
    module_path = module.replace(".", os.sep) + ".py"
    candidates = [
        module_path,
        os.path.join("mikiui_app_plugins", module_path),
    ]
    for candidate in candidates:
        if os.path.isfile(candidate):
            try:
                with open(candidate, encoding="utf-8") as fh:
                    return fh.read()
            except OSError:
                continue
    return None


__all__ = [
    "PluginMetadata",
    "discover_plugins",
    "discover_from_directory",
    "discover_from_entry_points",
    "load_plugin",
    "auto_load",
]
