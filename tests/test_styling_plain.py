"""Tests for plain CSS styling helpers."""

from __future__ import annotations

from mikiui.styling.plain_css import register_plain_theme, runtime_html, validate_plain_css_paths
from mikiui.styling.system import PlainCssConfig


def test_register_plain_theme_returns_dict():
    result = register_plain_theme()
    assert result["name"] == "light"
    assert result["source"] == "builtin-framework"
    assert result["framework"] == "css"


def test_plain_css_config_defaults():
    config = PlainCssConfig()
    assert config.framework.value == "plain"
    assert config.custom_css_paths == []


def test_runtime_html_contains_link():
    html = runtime_html(["https://example.com/style.css"])
    assert "<link" in html
    assert "https://example.com/style.css" in html


def test_validate_plain_css_paths_with_valid_files(tmp_path):
    css = tmp_path / "style.css"
    css.write_text("body {}")
    config = PlainCssConfig(custom_css_paths=[str(css)])
    warnings = validate_plain_css_paths(config, project_dir=tmp_path)
    assert warnings == []


def test_validate_plain_css_paths_skips_missing():
    config = PlainCssConfig(custom_css_paths=["nonexistent/style.css"])
    warnings = validate_plain_css_paths(config)
    assert len(warnings) == 1
    assert "not found" in warnings[0]
