"""Tests for engine diff and updater modules."""

from __future__ import annotations

import pytest

from mikiui.engine.diff import Swap, diff
from mikiui.engine.dom import Element, Text, RawHtml
from mikiui.engine.renderer import render_fragment
from mikiui.engine.updater import OptimisticUpdater


class FakeApp:
    def __init__(self, tree):
        self._tree = tree

    async def invoke(self, route, request=None):
        return self._tree, None


def test_diff_no_changes():
    old_el = Element("hello", id="x", class_="a")
    new_el = Element("hello", id="x", class_="a")
    assert diff(old_el, new_el) == []


def test_diff_updated_node():
    old_el = Element("old", id="x")
    new_el = Element("new", id="x")
    swaps = diff(old_el, new_el)
    assert len(swaps) == 1
    assert swaps[0].target_id == "x"
    assert swaps[0].swap == "outerHTML"
    assert 'id="x"' in swaps[0].html


def test_diff_added_node():
    old_el = Element("old", id="x")
    new_el = Element("new", id="y")
    swaps = diff(old_el, new_el)
    assert len(swaps) == 2
    ids = {s.target_id: s.swap for s in swaps}
    assert ids["y"] == "beforeend"
    assert ids["x"] == "outerHTML"


def test_diff_removed_node():
    old_el = Element("old", id="x")
    new_el = Element("new", id="y")
    swaps = diff(old_el, new_el)
    assert len(swaps) == 2
    ids = {s.target_id: s.swap for s in swaps}
    assert ids["y"] == "beforeend"
    assert ids["x"] == "outerHTML"
    assert swaps[1].html == ""


def test_diff_nested_trees():
    old_tree = Element(
        Element("a", id="keep"),
        Element("b", id="remove"),
    )
    new_tree = Element(
        Element("a", id="keep"),
        Element("c", id="add"),
    )
    swaps = diff(old_tree, new_tree)
    assert len(swaps) == 2
    ids = {s.target_id: s.swap for s in swaps}
    assert ids["add"] == "beforeend"
    assert ids["remove"] == "outerHTML"


def test_swap_dataclass():
    s = Swap(target_id="x", html="<div/>", swap="outerHTML")
    assert s.target_id == "x"
    assert s.swap == "outerHTML"


@pytest.mark.asyncio
async def test_updater_unwraps_tuple():
    tree = Element("ok", id="page")
    app = FakeApp(tree)
    updater = OptimisticUpdater(app)
    html = await updater.update(None)
    assert 'id="page"' in html
    assert "<div" in html
