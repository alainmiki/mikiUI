"""Tests for modal and layout primitive components."""

from __future__ import annotations

import pytest

from mikiui.components.layout_primitives import Column, Row, Spacer, Divider, Shape, Stack
from mikiui.components.modal import Modal
from mikiui.engine.dom import Element


def test_modal_defaults():
    m = Modal("Hello")
    assert m.tag == "div"
    assert 'role="dialog"' in m.to_html()
    assert 'aria-modal="true"' in m.to_html()
    assert "miki-modal" in m.to_html()


def test_modal_open_state():
    m = Modal("Hello", open=True)
    assert 'data-miki-modal-open="true"' in m.to_html()
    assert 'aria-hidden="false"' in m.to_html()
    m.open = False
    assert 'data-miki-modal-open="false"' in m.to_html()
    assert 'aria-hidden="true"' in m.to_html()


def test_modal_title():
    m = Modal("Content", title="Title")
    assert 'aria-labelledby="Title-modal-title"' in m.to_html()
    assert 'id="Title-modal-title"' in m.to_html()


def test_modal_size_variants():
    for size in ("xs", "sm", "md", "lg", "xl", "fullscreen"):
        m = Modal("", size=size)
        assert f"miki-modal-{size}" in m.to_html()
    m = Modal("", size="invalid")
    assert "miki-modal-md" in m.to_html()


def test_column_defaults():
    c = Column("a", "b")
    assert c.tag == "div"
    html = c.to_html()
    assert "miki-column" in html
    assert "display: flex" in html
    assert "flex-direction: column" in html


def test_column_gap_align_justify():
    c = Column("a", gap="1rem", align="center", justify="between")
    html = c.to_html()
    assert "gap: 1rem" in html
    assert "align-items: center" in html
    assert "justify-content: between" in html


def test_row_defaults():
    r = Row("a", "b")
    html = r.to_html()
    assert "miki-row" in html
    assert "flex-direction: row" in html


def test_row_wrap():
    r = Row("a", wrap=True)
    assert "miki-row-wrap" in r.to_html()
    assert "flex-wrap: wrap" in r.to_html()


def test_spacer():
    s = Spacer()
    assert s.tag == "div"
    html = s.to_html()
    assert "miki-spacer" in html
    assert "flex: 1 1 auto" in html


def test_divider_horizontal():
    d = Divider()
    assert d.tag == "hr"
    assert "miki-divider" in d.to_html()


def test_divider_vertical():
    d = Divider(orientation="vertical")
    assert "miki-divider-vertical" in d.to_html()
    assert "width: 1px" in d.to_html()


def test_divider_with_label():
    d = Divider(label="or")
    assert "miki-divider-with-label" in d.to_html()
    assert 'role="separator"' in d.to_html()


def test_shape_variants():
    for variant in ("rounded", "circle", "pill", "square", "none"):
        s = Shape(variant=variant)
        assert f"miki-shape-{variant}" in s.to_html()


def test_shape_size_and_background():
    s = Shape(size="3rem", background="red")
    html = s.to_html()
    assert "width: 3rem" in html
    assert "height: 3rem" in html
    assert "background: red" in html


def test_stack_defaults():
    s = Stack("a", "b")
    assert s.tag == "div"
    html = s.to_html()
    assert "miki-stack" in html
    assert "gap: 0.5rem" in html
