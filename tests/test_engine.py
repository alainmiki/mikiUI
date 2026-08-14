"""Tests for the MikiUI rendering engine (DOM model, i18n, page rendering)."""

from __future__ import annotations

import pytest

from mikiui.engine import (
    Element,
    Text,
    I18nText,
    _,
    render,
    normalize,
    set_translator,
    render_page,
)
from mikiui import Div, Span


def test_element_renders_tag_and_children():
    el = Element(Text("hello"), Span("world"))
    assert el.to_html() == "<div>hello<span>world</span></div>"


def test_element_escapes_text():
    el = Element("p", "<script>&")
    assert "&lt;script&gt;&amp;" in el.to_html()
    assert "<script>" not in el.to_html()


def test_class_underscore_mapping():
    el = Element("div", class_="box")
    assert 'class="box"' in el.to_html()


def test_aria_label_hyphen_mapping():
    el = Element("button", aria_label="Close")
    assert 'aria-label="Close"' in el.to_html()


def test_hx_get_hyphen_mapping():
    el = Element("a", hx_get="/next")
    assert 'hx-get="/next"' in el.to_html()


def test_style_dict_serialized():
    el = Element("div", style={"color": "red", "margin": "0"})
    html = el.to_html()
    assert "color:red" in html
    assert "margin:0" in html


def test_boolean_attr_valueless():
    el = Element("input", disabled=True)
    assert "disabled" in el.to_html()


def test_none_and_false_attrs_omitted():
    el = Element("div", hidden=None, visible=False, data_x="1")
    html = el.to_html()
    assert "hidden" not in html
    assert "visible" not in html
    assert 'data-x="1"' in html


def test_i18n_translation_applied():
    set_translator(lambda key, default: default.upper())
    try:
        node = _("greeting", "hello")
        assert isinstance(node, I18nText)
        html = node.to_html()
        assert 'data-i18n="greeting"' in html
        assert "HELLO" in html
    finally:
        set_translator(None)


def test_i18n_default_without_translator():
    set_translator(None)
    html = _("greeting", "Hello").to_html()
    assert "Hello" in html
    assert 'data-i18n="greeting"' in html


def test_normalize_wraps_scalar():
    div = Element("div")
    assert normalize(div) == [div]
    assert normalize(None) == []
    assert normalize([div, None, div]) == [div, div]
    assert normalize("x") == ["x"]


def test_render_dispatches():
    assert render(Text("<b>")) == "&lt;b&gt;"
    assert render(Element("x")) == "<div>x</div>"


def test_render_page_contains_doctype_and_css():
    page = render_page(Div("content"), title="My App", lang="en")
    assert "<!doctype html>" in page
    assert "miki.css" in page
    assert "<div>content</div>" in page
    assert "<title>My App</title>" in page
