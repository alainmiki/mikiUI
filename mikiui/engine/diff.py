"""Tree diffing for optimistic / partial updates.

Given two rendered HTML trees (or lists of nodes), produces the minimal set of
swap instructions an HTMX client can apply. For the MVP this is a simple,
attribute-and-children based diff keyed by element ``id``; it is intentionally
small and dependency-free.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .dom import Element, render


@dataclass
class Swap:
    """An instruction to replace the element with ``target_id`` with ``html``."""

    target_id: str
    html: str
    swap: str = "innerHTML"


def diff(old: Any, new: Any) -> list[Swap]:
    """Return swap instructions to turn ``old`` into ``new``.

    Only elements carrying an ``id`` are diffed (HTMX swaps are id-targeted).
    Two elements with the same id but different serialized HTML produce a swap.
    Added and removed elements are also reported.
    """
    old_by_id = _index(old)
    new_by_id = _index(new)
    swaps: list[Swap] = []
    seen_ids: set[str] = set()

    for id_, node in new_by_id.items():
        seen_ids.add(id_)
        if id_ not in old_by_id:
            swaps.append(Swap(target_id=id_, html=render(node), swap="beforeend"))
            continue
        if render(node) != render(old_by_id[id_]):
            swaps.append(Swap(target_id=id_, html=render(node), swap="outerHTML"))

    for id_, node in old_by_id.items():
        if id_ not in seen_ids:
            swaps.append(Swap(target_id=id_, html="", swap="outerHTML"))

    return swaps


def _index(node: Any, acc: dict[str, Element] | None = None) -> dict[str, Element]:
    if acc is None:
        acc = {}
    if isinstance(node, Element):
        if "id" in node.attrs and node.attrs["id"]:
            acc[str(node.attrs["id"])] = node
        for child in node.children:
            _index(child, acc)
    elif isinstance(node, (list, tuple)):
        for child in node:
            _index(child, acc)
    return acc
