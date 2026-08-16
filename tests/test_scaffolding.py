"""Tests for the CLI scaffolding and framework selection."""

from __future__ import annotations

import tempfile

from mikiui.cli.scaffolding import UI_FRAMEWORKS, framework_config, scaffold


def _scaffold_in_temp(framework: str = "tailwind") -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = scaffold(f"testapp_{framework}", directory=tmp, framework=framework)
        # Read files before the temp directory is cleaned up.
        app_py = (path / "app.py").read_text(encoding="utf-8")
        readme = (path / "README.md").read_text(encoding="utf-8")
        files = {f.name for f in path.iterdir()}
        yield app_py, readme, files


def test_ui_frameworks_list():
    """UI_FRAMEWORKS should include all supported frameworks."""
    assert set(UI_FRAMEWORKS) == {"tailwind", "bootstrap", "daisyui", "plain"}


def test_framework_config_returns_valid_python():
    """framework_config should return valid Python code for each framework."""
    for fw in UI_FRAMEWORKS:
        config_line = framework_config(fw)
        assert "set_theme" in config_line
        assert config_line.strip().startswith("app.set_theme(")


def test_scaffold_creates_app_py():
    """scaffold should create an app.py with the project name as title."""
    for app_py, _, _ in _scaffold_in_temp("tailwind"):
        assert 'title="testapp_tailwind"' in app_py
        assert "MikiApp" in app_py


def test_scaffold_tailwind_includes_config():
    """Tailwind framework should include tailwind.config.js and postcss.config.js."""
    for _, _, files in _scaffold_in_temp("tailwind"):
        assert "tailwind.config.js" in files
        assert "postcss.config.js" in files


def test_scaffold_daisyui_includes_config():
    """DaisyUI framework should include Tailwind/PostCSS config files."""
    for _, _, files in _scaffold_in_temp("daisyui"):
        assert "tailwind.config.js" in files
        assert "postcss.config.js" in files


def test_scaffold_bootstrap_no_tailwind_config():
    """Bootstrap framework should NOT include tailwind.config.js."""
    for _, _, files in _scaffold_in_temp("bootstrap"):
        assert "tailwind.config.js" not in files


def test_scaffold_plain_no_tailwind_config():
    """Plain framework should NOT include tailwind.config.js."""
    for _, _, files in _scaffold_in_temp("plain"):
        assert "tailwind.config.js" not in files


def test_scaffold_sets_correct_theme():
    """Each framework should set the correct theme in the generated app."""
    expected = {
        "tailwind": '"tailwind"',
        "bootstrap": '"bootstrap"',
        "daisyui": '"tailwind"',
        "plain": '"light"',
    }
    for fw, theme in expected.items():
        for app_py, _, _ in _scaffold_in_temp(fw):
            assert f'app.set_theme({theme})' in app_py


def test_scaffold_raises_for_invalid_framework():
    """scaffold should reject unknown frameworks."""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            scaffold("badapp", directory=tmp, framework="unknown")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_scaffold_creates_readme_with_framework():
    """README should mention the framework."""
    for _, readme, _ in _scaffold_in_temp("bootstrap"):
        assert "bootstrap" in readme.lower()


def test_scaffold_creates_requirements():
    """scaffold should create a requirements.txt."""
    for _, _, files in _scaffold_in_temp("tailwind"):
        assert "requirements.txt" in files


def test_scaffold_raises_for_existing_directory():
    """scaffold should raise FileExistsError if the target already exists."""
    with tempfile.TemporaryDirectory() as tmp:
        scaffold("existing", directory=tmp, framework="plain")
        try:
            scaffold("existing", directory=tmp, framework="plain")
            assert False, "Should have raised FileExistsError"
        except FileExistsError:
            pass
