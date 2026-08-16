"""Tests for DOM sanitization utilities."""

from __future__ import annotations

from mikiui.engine.dom import Element, Text, _render_child, escape_attr, sanitize_html, truncate


class TestSanitizeHtml:
    def test_strips_script_tags(self):
        result = sanitize_html("<script>alert(1)</script>")
        assert "<script>" not in result
        assert "</script>" not in result

    def test_strips_iframe_tags(self):
        assert "<iframe>" not in sanitize_html("<iframe src='x'></iframe>")

    def test_strips_onclick_attr(self):
        result = sanitize_html('<div onclick="alert(1)">hello</div>')
        assert "onclick" not in result

    def test_allowlist_tags(self):
        result = sanitize_html("<b>bold</b><script>bad</script>", allow_tags=["b"])
        assert "<b>bold</b>" in result
        assert "<script>" not in result

    def test_plain_text_unchanged(self):
        text = "hello world"
        assert sanitize_html(text) == text


class TestEscapeAttr:
    def test_escapes_quotes(self):
        assert '"' not in escape_attr('hello"world')

    def test_escapes_ampersand(self):
        assert "&amp;" in escape_attr("a & b")

    def test_escapes_less_than(self):
        assert "&lt;" in escape_attr("a < b")


class TestTruncate:
    def test_short_text(self):
        assert truncate("hello", length=10) == "hello"

    def test_long_text(self):
        result = truncate("hello world", length=8)
        assert len(result) == 8
        assert result.endswith("...")

    def test_custom_suffix(self):
        result = truncate("hello world", length=10, suffix="…")
        assert result.endswith("…")


class TestRenderChildSanitization:
    def test_html_string_sanitized(self):
        result = _render_child("<script>alert(1)</script>")
        assert "<script>" not in result

    def test_plain_string_escaped(self):
        result = _render_child("<b>bold</b>")
        assert "&lt;b&gt;bold&lt;/b&gt;" in result


class TestTextEscaping:
    def test_escapes_html(self):
        t = Text("<script>")
        assert "<script>" not in t.to_html()


class TestElementAttrEscaping:
    def test_escapes_attr_value(self):
        el = Element("div", title='hello"world')
        assert 'title="hello&amp;quot;world"' not in el.to_html()
        assert 'title="hello&quot;world"' in el.to_html()
