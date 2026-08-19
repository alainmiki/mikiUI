"""Tests for plugin security, manifest validation, and sandboxing."""

from __future__ import annotations

import ast
import textwrap

import pytest

from mikiui.app.plugin_security import (
    PluginManifest,
    PluginSecurityConfig,
    PluginSecurityViolation,
    PluginValidator,
    _check_ast,
    _extract_imports,
    load_manifest,
    validate_plugin,
)
from mikiui.app.plugins import Plugin

# ---------------------------------------------------------------------------
# PluginSecurityConfig defaults
# ---------------------------------------------------------------------------

def test_default_security_config_blocks_dangerous_imports():
    config = PluginSecurityConfig()
    assert "subprocess" in config.blocked_imports
    assert "eval" in config.blocked_imports
    assert "os.system" in config.blocked_imports


def test_default_security_config_vet_ast_enabled():
    config = PluginSecurityConfig()
    assert config.vet_ast is True


def test_default_security_config_disallows_untrusted():
    config = PluginSecurityConfig()
    assert config.allow_untrusted is False


# ---------------------------------------------------------------------------
# PluginManifest
# ---------------------------------------------------------------------------

def test_manifest_required_fields():
    with pytest.raises(TypeError):
        PluginManifest(name="test")  # missing required fields


def test_manifest_from_module_attributes():
    import types

    module = types.ModuleType("fake_plugin")
    module.__name__ = "fake_plugin"
    module.__version__ = "1.2.3"
    module.__doc__ = "A fake plugin."

    manifest = load_manifest(module)
    assert manifest is not None
    assert manifest.name == "fake_plugin"
    assert manifest.version == "1.2.3"
    assert "A fake plugin" in manifest.description


def test_manifest_from_plugin_json(tmp_path):
    plugin_dir = tmp_path / "myplugin"
    plugin_dir.mkdir()
    (plugin_dir / "plugin.json").write_text(
        '{"name": "json-plugin", "version": "2.0.0", "description": "From JSON.", '
        '"author": "Tester", "license": "MIT", "capabilities": ["network:outbound"]}'
    )
    (plugin_dir / "__init__.py").write_text("")
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "json_plugin", plugin_dir / "__init__.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = load_manifest(module)
    assert result is not None
    assert result.name == "json-plugin"
    assert result.version == "2.0.0"
    assert result.capabilities == ["network:outbound"]


# ---------------------------------------------------------------------------
# PluginValidator
# ---------------------------------------------------------------------------

def test_validator_rejects_empty_name():
    class BadPlugin(Plugin):
        name = ""

    with pytest.raises(PluginSecurityViolation, match="non-empty name"):
        PluginValidator().validate_plugin(BadPlugin())


def test_validator_rejects_manifest_name_mismatch():
    class MyPlugin(Plugin):
        name = "my-plugin"
        manifest = PluginManifest(
            name="other-plugin",
            version="1.0.0",
            description="x",
            author="a",
            license="MIT",
        )

    with pytest.raises(PluginSecurityViolation, match="does not match manifest"):
        PluginValidator().validate_plugin(MyPlugin(), manifest=MyPlugin.manifest)


def test_validator_rejects_blocked_capability():
    class LoudPlugin(Plugin):
        name = "loud"
        capabilities = ["network:outbound"]

    config = PluginSecurityConfig(blocked_capabilities=["network:outbound"])
    with pytest.raises(PluginSecurityViolation, match="blocked capability"):
        PluginValidator(config).validate_plugin(LoudPlugin())


def test_validator_accepts_clean_plugin():
    class CleanPlugin(Plugin):
        name = "clean"
        capabilities = ["ui:render"]

    # Should not raise.
    PluginValidator().validate_plugin(CleanPlugin())


# ---------------------------------------------------------------------------
# AST vetting
# ---------------------------------------------------------------------------

def test_ast_vet_blocks_subprocess_run():
    source = textwrap.dedent(
        """
        import subprocess
        subprocess.run(["ls"])
        """
    )
    tree = ast.parse(source)
    violations = _check_ast(tree)
    assert any("subprocess.run" in v for v in violations)


def test_ast_vet_blocks_os_system():
    source = textwrap.dedent(
        """
        import os
        os.system("rm -rf /")
        """
    )
    tree = ast.parse(source)
    violations = _check_ast(tree)
    assert any("os.system" in v for v in violations)


def test_ast_vet_blocks_eval():
    source = textwrap.dedent(
        """
        x = eval("1+1")
        """
    )
    tree = ast.parse(source)
    violations = _check_ast(tree)
    assert any("eval" in v for v in violations)


def test_ast_vet_blocks_importlib_import_module():
    source = textwrap.dedent(
        """
        import importlib
        importlib.import_module("os")
        """
    )
    tree = ast.parse(source)
    violations = _check_ast(tree)
    assert any("importlib.import_module" in v for v in violations)


def test_ast_vet_allows_safe_code():
    source = textwrap.dedent(
        """
        from mikiui import Div
        import logging

        class SafePlugin(Plugin):
            name = "safe"
        """
    )
    tree = ast.parse(source)
    violations = _check_ast(tree)
    assert violations == []


def test_ast_vet_blocks_shutil_rmtree():
    source = textwrap.dedent(
        """
        import shutil
        shutil.rmtree("/tmp")
        """
    )
    tree = ast.parse(source)
    violations = _check_ast(tree)
    assert any("shutil.rmtree" in v for v in violations)


# ---------------------------------------------------------------------------
# Import scanning
# ---------------------------------------------------------------------------

def test_extract_imports_basic():
    source = textwrap.dedent(
        """
        import os
        import json
        from mikiui import Div
        from typing import Optional
        """
    )
    tree = ast.parse(source)
    imports = _extract_imports(tree)
    assert "os" in imports
    assert "json" in imports
    assert "mikiui" in imports
    assert "typing" in imports


def test_validator_blocks_blocked_import():
    class BlockedPlugin(Plugin):
        name = "blocked"

    source = textwrap.dedent(
        """
        import subprocess
        """
    )
    with pytest.raises(PluginSecurityViolation, match="blocked modules"):
        PluginValidator().validate_plugin(
            BlockedPlugin(), source_code=source
        )


def test_validator_allows_safe_imports():
    class SafePlugin(Plugin):
        name = "safe"

    source = textwrap.dedent(
        """
        import json
        from mikiui import Div
        """
    )
    # Should not raise.
    PluginValidator().validate_plugin(SafePlugin(), source_code=source)


# ---------------------------------------------------------------------------
# Validator integration with Plugin class
# ---------------------------------------------------------------------------

def test_validate_plugin_convenience_function():
    class MyPlugin(Plugin):
        name = "my-plugin"

    # Should not raise.
    validate_plugin(MyPlugin())


def test_validate_plugin_with_custom_config():
    class MyPlugin(Plugin):
        name = "my-plugin"
        capabilities = ["network:outbound"]

    config = PluginSecurityConfig(blocked_capabilities=["network:outbound"])
    with pytest.raises(PluginSecurityViolation):
        validate_plugin(MyPlugin(), config=config)
