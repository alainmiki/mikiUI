"""Tests for the MikiUI plugin marketplace."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from mikiui.app.marketplace import (
    DirectoryIndexSource,
    PluginInfo,
    PluginMarketplace,
)
from mikiui.app.plugin_security import PluginSecurityConfig, PluginSecurityViolation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_plugin_package(base: str, name: str, *, manifest_capabilities=None, class_name=None):
    """Write a minimal plugin package under *base*/*name*."""
    pkg_dir = os.path.join(base, name)
    os.makedirs(pkg_dir, exist_ok=True)
    caps = manifest_capabilities or []
    manifest = {
        "name": name,
        "version": "1.0.0",
        "description": f"A {name} plugin.",
        "author": "Tester",
        "license": "MIT",
        "capabilities": caps,
    }
    with open(os.path.join(pkg_dir, "plugin.json"), "w") as fh:
        json.dump(manifest, fh)
    safe_name = name.replace("-", "_")
    cls_name = class_name or f"{name.replace('-', '_').capitalize()}Plugin"
    module_file = os.path.join(pkg_dir, f"{safe_name}.py")
    with open(module_file, "w") as fh:
        fh.write(
            f"class {cls_name}:\n"
            f"    name = {name!r}\n"
            f"    capabilities = {caps!r}\n"
        )
    return pkg_dir


# ---------------------------------------------------------------------------
# PluginInfo
# ---------------------------------------------------------------------------

def test_plugin_info_defaults():
    info = PluginInfo(
        name="test", version="1.0.0", description="desc", author="me", license="MIT"
    )
    assert info.source == "unknown"
    assert info.capabilities == []


# ---------------------------------------------------------------------------
# DirectoryIndexSource
# ---------------------------------------------------------------------------

def test_directory_index_source_lists_plugins():
    with tempfile.TemporaryDirectory() as tmp:
        _write_plugin_package(tmp, "alpha")
        _write_plugin_package(tmp, "beta")
        source = DirectoryIndexSource(tmp)
        results = source.list_all()
        names = {p.name for p in results}
        assert "alpha" in names
        assert "beta" in names


def test_directory_index_source_search_filters():
    with tempfile.TemporaryDirectory() as tmp:
        _write_plugin_package(tmp, "chart-plugin")
        _write_plugin_package(tmp, "auth-plugin")
        source = DirectoryIndexSource(tmp)
        results = source.search("chart")
        assert len(results) == 1
        assert results[0].name == "chart-plugin"


def test_directory_index_source_fetch_copies_package():
    with tempfile.TemporaryDirectory() as tmp:
        _write_plugin_package(tmp, "alpha")
        source = DirectoryIndexSource(tmp)
        dest = os.path.join(tmp, "installed")
        result = source.fetch("alpha", dest)
        assert os.path.isdir(result)
        assert os.path.isfile(os.path.join(result, "plugin.json"))
        assert os.path.isfile(os.path.join(result, "alpha.py"))


def test_directory_index_source_fetch_missing_raises():
    with tempfile.TemporaryDirectory() as tmp:
        source = DirectoryIndexSource(tmp)
        with pytest.raises(FileNotFoundError):
            source.fetch("nonexistent", os.path.join(tmp, "out"))


# ---------------------------------------------------------------------------
# PluginMarketplace
# ---------------------------------------------------------------------------

def test_marketplace_search():
    with tempfile.TemporaryDirectory() as tmp:
        _write_plugin_package(tmp, "chart-plugin")
        _write_plugin_package(tmp, "auth-plugin")
        source = DirectoryIndexSource(tmp)
        market = PluginMarketplace(source)
        results = market.search("chart")
        assert len(results) == 1
        assert results[0].name == "chart-plugin"


def test_marketplace_install_validates_plugin():
    with tempfile.TemporaryDirectory() as tmp:
        _write_plugin_package(tmp, "safe-plugin")
        source = DirectoryIndexSource(tmp)
        config = PluginSecurityConfig(vet_ast=True, allow_untrusted=True)
        market = PluginMarketplace(source, security_config=config)

        from mikiui.app.app import MikiApp

        app = MikiApp(title="Test")
        app.set_plugin_security_config(config)
        plugin = market.install("safe-plugin", app)
        assert plugin.name == "safe-plugin"
        assert len(app.plugins) == 1


def test_marketplace_install_rejects_dangerous_plugin():
    with tempfile.TemporaryDirectory() as tmp:
        pkg_dir = os.path.join(tmp, "evil")
        os.makedirs(pkg_dir, exist_ok=True)
        with open(os.path.join(pkg_dir, "plugin.json"), "w") as fh:
            json.dump(
                {
                    "name": "evil",
                    "version": "1.0.0",
                    "description": "evil",
                    "author": "x",
                    "license": "MIT",
                },
                fh,
            )
        # Write a module that imports a blocked module (subprocess).
        with open(os.path.join(pkg_dir, "evil.py"), "w") as fh:
            fh.write(
                "class EvilPlugin:\n"
                "    name = 'evil'\n"
                "    capabilities = []\n"
                "\n"
                "import subprocess\n"
            )

        source = DirectoryIndexSource(tmp)
        config = PluginSecurityConfig(vet_ast=True, allow_untrusted=True)
        market = PluginMarketplace(source, security_config=config)

        from mikiui.app.app import MikiApp

        app = MikiApp(title="Test")
        app.set_plugin_security_config(config)
        with pytest.raises(PluginSecurityViolation):
            market.install("evil", app)
        assert len(app.plugins) == 0


def test_marketplace_install_all():
    with tempfile.TemporaryDirectory() as tmp:
        _write_plugin_package(tmp, "alpha")
        _write_plugin_package(tmp, "beta")
        source = DirectoryIndexSource(tmp)
        config = PluginSecurityConfig(vet_ast=True, allow_untrusted=True)
        market = PluginMarketplace(source, security_config=config)

        from mikiui.app.app import MikiApp

        app = MikiApp(title="Test")
        app.set_plugin_security_config(config)
        installed = market.install_all(app)
        names = {p.name for p in installed}
        assert "alpha" in names
        assert "beta" in names
