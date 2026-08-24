"""Marketplace client for MikiUI plugins.

The marketplace layer provides a pluggable backend for discovering, auditing,
and installing plugins from remote or local indexes.  The built-in backend is
a simple directory-based index (``mikiui_plugins/``), but the abstract
:class:`MarketplaceSource` allows swapping in a remote HTTP index, a PyPI-like
server, or a private registry.

Typical usage::

    from mikiui.app.marketplace import (
        PluginMarketplace,
        PluginInfo,
        DirectoryIndexSource,
    )

    source = DirectoryIndexSource("mikiui_plugins")
    marketplace = PluginMarketplace(source)

    results = marketplace.search("chart")
    for info in results:
        print(info.name, info.version, info.description)

    # Install (download + register)
    plugin = marketplace.install("my-chart-plugin", app)
    app.use(plugin)

Security
--------
Every plugin downloaded from a marketplace is validated through
:class:`~mikiui.app.plugin_security.PluginValidator` before it is loaded.
The app's :class:`~mikiui.app.MikiApp` security policy (``allow_untrusted``,
``vet_ast``, ``blocked_capabilities``) applies.  Plugins that fail validation
raise :class:`~mikiui.app.plugin_security.PluginSecurityViolation` and are
**not installed**.
"""

from __future__ import annotations

import logging
import re
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from ..app.plugin_discovery import discover_plugins
from ..app.plugin_security import (
    PluginManifest,
    PluginSecurityConfig,
    PluginValidator,
    load_manifest,
)
from ..app.plugins import Plugin

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Marketplace data types
# ---------------------------------------------------------------------------

@dataclass
class PluginInfo:
    """Metadata for a plugin available in the marketplace.

    Attributes:
        name: Unique plugin identifier.
        version: Semver string.
        description: Human-readable description.
        author: Maintainer name.
        license: SPDX license identifier.
        capabilities: Declared capabilities.
        source: Where the plugin is hosted (``"local"``, ``"directory"``,
            ``"pypi"``, ``"http"``).
        download_url: URL to download the plugin package.
        checksum: SHA-256 checksum of the downloadable package.
        manifest: Full plugin manifest (if available).
    """

    name: str
    version: str
    description: str
    author: str
    license: str
    capabilities: list[str] = field(default_factory=list)
    source: str = "unknown"
    download_url: str | None = None
    checksum: str | None = None
    manifest: PluginManifest | None = None


# ---------------------------------------------------------------------------
# Marketplace source backends
# ---------------------------------------------------------------------------

class MarketplaceSource(ABC):
    """Abstract base for marketplace index backends."""

    @abstractmethod
    def search(self, query: str) -> list[PluginInfo]:
        """Return plugins matching *query*."""

    @abstractmethod
    def fetch(self, name: str, dest: Path) -> Path:
        """Download plugin *name* into *dest* and return the plugin dir path."""

    @abstractmethod
    def list_all(self) -> list[PluginInfo]:
        """Return every available plugin."""


class DirectoryIndexSource(MarketplaceSource):
    """A marketplace backed by a local directory of plugin packages.

    Each sub-directory of *index_dir* is treated as a plugin package and
    should contain a ``plugin.json`` manifest (optional) and the plugin
    module(s).

    Parameters
    ----------
    index_dir:
        Path to the directory containing plugin packages.
    """

    def __init__(self, index_dir: str | Path) -> None:
        self.index_dir = Path(index_dir)

    def search(self, query: str) -> list[PluginInfo]:
        query_lower = query.lower()
        results = []
        for info in self.list_all():
            if query_lower in info.name.lower() or query_lower in info.description.lower():
                results.append(info)
        return results

    def fetch(self, name: str, dest: Path) -> Path:
        dest = Path(dest)
        src = self.index_dir / name
        if not src.is_dir():
            raise FileNotFoundError(f"Plugin {name!r} not found in {self.index_dir}.")
        dest.mkdir(parents=True, exist_ok=True)
        target = dest / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(src, target)
        return target

    def list_all(self) -> list[PluginInfo]:
        results: list[PluginInfo] = []
        if not self.index_dir.is_dir():
            return results
        for entry in sorted(self.index_dir.iterdir()):
            if not entry.is_dir() or entry.name.startswith("_"):
                continue
            manifest = _load_manifest_from_dir(entry)
            if manifest is None:
                continue
            results.append(
                PluginInfo(
                    name=manifest.name,
                    version=manifest.version,
                    description=manifest.description,
                    author=manifest.author,
                    license=manifest.license,
                    capabilities=list(manifest.capabilities),
                    source="directory",
                    download_url=None,
                    checksum=manifest.checksum,
                    manifest=manifest,
                )
            )
        return results


class PyPIIndexSource(MarketplaceSource):
    """A marketplace backed by a PyPI-like JSON API.

    Parameters
    ----------
    base_url:
        Base URL of the JSON API (e.g. ``"https://pypi.org/pypi"``).
    """

    def __init__(self, base_url: str = "https://pypi.org/pypi") -> None:
        self.base_url = base_url.rstrip("/")

    def search(self, query: str) -> list[PluginInfo]:  # pragma: no cover - network
        import json
        import urllib.error
        import urllib.request

        url = f"{self.base_url}?q={query}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
        except (OSError, ValueError):
            return []
        results = []
        for item in data.get("projects", []) if isinstance(data, dict) else data:
            if not isinstance(item, dict):
                continue
            results.append(
                PluginInfo(
                    name=item.get("name", ""),
                    version=item.get("version", "0.0.0"),
                    description=item.get("description", ""),
                    author=item.get("author", "unknown"),
                    license=item.get("license", "MIT"),
                    source="pypi",
                    download_url=item.get("url"),
                )
            )
        return results

    def fetch(self, name: str, dest: Path) -> Path:  # pragma: no cover - network
        dest = Path(dest)
        import io
        import urllib.request
        import zipfile

        url = f"{self.base_url}/{name}/download"
        dest.mkdir(parents=True, exist_ok=True)
        target = dest / name
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read()
            if url.endswith(".zip") or name.endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(data)) as zf:
                    zf.extractall(target)
            else:
                (target / "__init__.py").write_bytes(data)
        except OSError as exc:
            raise FileNotFoundError(f"Failed to download {name!r}: {exc}") from exc
        return target

    def list_all(self) -> list[PluginInfo]:  # pragma: no cover - network
        import json
        import urllib.request

        url = f"{self.base_url}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read())
        except (OSError, ValueError):
            return []
        results = []
        for item in data.get("projects", []) if isinstance(data, dict) else data:
            if not isinstance(item, dict):
                continue
            results.append(
                PluginInfo(
                    name=item.get("name", ""),
                    version=item.get("version", "0.0.0"),
                    description=item.get("description", ""),
                    author=item.get("author", "unknown"),
                    license=item.get("license", "MIT"),
                    source="pypi",
                    download_url=item.get("url"),
                )
            )
        return results


# ---------------------------------------------------------------------------
# Marketplace client
# ---------------------------------------------------------------------------

class PluginMarketplace:
    """Client for searching and installing plugins from a marketplace source.

    Parameters
    ----------
    source:
        The marketplace index backend.
    security_config:
        Optional security policy applied to every plugin before it is loaded.
        When omitted the default :class:`PluginSecurityConfig` is used.
    """

    def __init__(
        self,
        source: MarketplaceSource,
        security_config: PluginSecurityConfig | None = None,
    ) -> None:
        self.source = source
        self.security_config = security_config or PluginSecurityConfig()
        self._validator = PluginValidator(self.security_config)

    def search(self, query: str) -> list[PluginInfo]:
        """Search the marketplace for plugins matching *query*."""
        return self.source.search(query)

    def list_all(self) -> list[PluginInfo]:
        """List every available plugin."""
        return self.source.list_all()

    def install(self, name: str, app: Any, *, dest: Path | str | None = None) -> Plugin:
        """Download and register plugin *name* on *app*.

        Parameters
        ----------
        name:
            Plugin identifier.
        app:
            The :class:`~mikiui.app.MikiApp` instance to register on.
        dest:
            Temporary download directory.  Defaults to ``.mikiui/plugins``.

        Returns
        -------
        Plugin
            The registered plugin instance.

        Raises
        ------
        PluginSecurityViolation
            If the plugin fails validation.
        FileNotFoundError
            If the plugin is not found in the marketplace.
        """
        dest = Path(dest) if dest is not None else Path(".mikiui") / "plugins"
        plugin_dir = self.source.fetch(name, dest)
        # Discover + load the plugin from the downloaded directory.
        metas = discover_plugins(
            include_builtins=False,
            plugin_dirs=[plugin_dir],
            include_entry_points=False,
        )
        if not metas:
            raise FileNotFoundError(
                f"Plugin {name!r} was downloaded but no Plugin subclass was found."
            )
        meta = metas[0]
        plugin_cls = _load_from_dir(plugin_dir, meta)
        if plugin_cls is None:
            raise FileNotFoundError(
                f"Plugin {name!r} class {meta.class_name!r} could not be loaded."
            )
        plugin = cast(Plugin, plugin_cls())
        # Validate before registering.
        manifest = load_manifest(_resolve_module_from_dir(plugin_dir, meta))
        self._validator.validate_plugin(
            plugin,
            manifest=manifest,
            source_code=_read_source_from_dir(plugin_dir, meta),
        )
        app.use(plugin)
        logger.info("Installed plugin %r from marketplace.", name)
        return plugin

    def install_all(self, app: Any, *, dest: Path | None = None) -> list[Plugin]:
        """Install every available plugin that passes validation.

        Returns the list of successfully registered plugins.
        """
        installed = []
        for info in self.list_all():
            try:
                plugin = self.install(info.name, app, dest=dest)
                installed.append(plugin)
            except Exception:
                logger.exception("Failed to install plugin %r.", info.name)
        return installed


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_manifest_from_dir(plugin_dir: Path) -> PluginManifest | None:
    candidate = plugin_dir / "plugin.json"
    if candidate.is_file():
        try:
            import json

            with open(candidate, encoding="utf-8") as fh:
                raw = json.load(fh)
            return PluginManifest(**raw)
        except Exception:
            pass
    # Fall back: scan .py files.
    from ..app.plugin_discovery import discover_from_directory

    metas = discover_from_directory(plugin_dir)
    for meta in metas:
        if meta.class_name:
            manifest = PluginManifest(
                name=meta.name,
                version=meta.version,
                description=meta.description,
                author="unknown",
                license="MIT",
                dependencies=list(meta.dependencies),
                source="directory",
            )
            return manifest
    return None


def _load_from_dir(plugin_dir: Path, meta: Any) -> type | None:
    """Import a plugin class from a downloaded plugin directory.

    Uses duck typing: a plugin class is any callable class with a non-empty
    ``name`` attribute.  This avoids requiring the plugin module to import
    ``mikiui.app.plugins.Plugin`` during discovery.
    """
    import importlib.util
    import sys

    for candidate in plugin_dir.rglob("*.py"):
        if candidate.name.startswith("_") or candidate.name == "__init__.py":
            continue
        dotted = candidate.relative_to(plugin_dir).with_suffix("").as_posix().replace("/", ".")
        # Sanitize dotted name to valid Python identifier.
        sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", dotted)
        spec = importlib.util.spec_from_file_location(sanitized, candidate)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules[sanitized] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(sanitized, None)
            continue
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and attr_name not in {"Plugin", "object"}
                and hasattr(attr, "name")
            ):
                # Duck-typing: any class with a `name` attr is a plugin.
                return attr
    return None


def _resolve_module_from_dir(plugin_dir: Path, meta: Any) -> Any:
    """Return the module object for a discovered plugin meta."""
    import importlib.util
    import sys

    for candidate in plugin_dir.rglob("*.py"):
        if candidate.name.startswith("_") or candidate.name == "__init__.py":
            continue
        dotted = candidate.relative_to(plugin_dir).with_suffix("").as_posix().replace("/", ".")
        if dotted == meta.module_path or dotted.endswith(meta.class_name):
            spec = importlib.util.spec_from_file_location(dotted, candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[dotted] = module
            try:
                spec.loader.exec_module(module)
                return module
            except Exception:
                sys.modules.pop(dotted, None)
    return None


def _read_source_from_dir(plugin_dir: Path, meta: Any) -> str | None:
    """Read raw source code for a plugin from a downloaded directory."""
    for candidate in plugin_dir.rglob("*.py"):
        if candidate.name.startswith("_") or candidate.name == "__init__.py":
            continue
        dotted = candidate.relative_to(plugin_dir).with_suffix("").as_posix().replace("/", ".")
        if dotted == meta.module_path or dotted.endswith(meta.class_name):
            try:
                return candidate.read_text(encoding="utf-8")
            except OSError:
                return None
    return None


__all__ = [
    "PluginInfo",
    "MarketplaceSource",
    "DirectoryIndexSource",
    "PyPIIndexSource",
    "PluginMarketplace",
]
