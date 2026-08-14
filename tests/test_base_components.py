"""Tests for the missing base/HTML components."""

from __future__ import annotations

import pytest

from mikiui.components import (
    Accordion,
    Breadcrumbs,
    Cite,
    Figcaption,
    Figure,
    MenuItem,
    Picture,
    Samp,
    Tooltip,
    Var,
)
from mikiui.components.html import Source


def test_picture_contains_picture_and_img():
    node = Picture("cat.png", "A cat", Source(srcset="cat.webp", type="image/webp"))
    html = node.to_html()
    assert "<picture>" in html
    assert 'src="cat.png"' in html
    assert 'alt="A cat"' in html
    assert "<img" in html
    assert "<source" in html


def test_accordion_contains_details_summary():
    node = Accordion([("Title", "Body"), ("Title2", "Body2")])
    html = node.to_html()
    assert 'role="list"' in html
    assert "<details" in html
    assert "<summary" in html
    assert "Title" in html
    assert "Body" in html


def test_tooltip_contains_title_and_data():
    node = Tooltip("Hover me", "Helpful tip")
    html = node.to_html()
    assert "title=" in html
    assert "Helpful tip" in html
    assert "data-tooltip=" in html
    assert "Hover me" in html


def test_breadcrumbs_accessible_and_links():
    node = Breadcrumbs([("home", "Home"), ("about", "About")])
    html = node.to_html()
    assert 'aria-label="breadcrumb"' in html
    assert "<nav" in html
    assert "<ol>" in html
    assert 'href="home"' in html
    assert ">Home<" in html
    # last item is non-link text
    assert "About" in html


def test_menuitem_tag():
    html = MenuItem("Copy").to_html()
    assert "<menuitem" in html
    assert "Copy" in html


def test_semantic_tags():
    assert "<figure" in Figure("x").to_html()
    assert "<figcaption" in Figcaption("x").to_html()
    assert "<cite>" in Cite("x").to_html()
    assert "<var>" in Var("x").to_html()
    assert "<samp>" in Samp("x").to_html()
