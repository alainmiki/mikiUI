"""Optimistic updater.

Wraps a route handler so its result is rendered and (when the request is an
HTMX partial) returned with the swap instructions computed by ``engine.diff``.
This lets handlers return a full tree while the client only patches changed
regions identified by element ``id``.
"""

from __future__ import annotations

from typing import Any

from .diff import diff
from .renderer import render_fragment


class OptimisticUpdater:
    def __init__(self, app: Any) -> None:
        self.app = app

    async def update(self, route, request: Any = None) -> str:
        result = await self.app.invoke(route, request)
        if isinstance(result, tuple):
            nodes = result[0]
        else:
            nodes = result
        return render_fragment(nodes)

    @staticmethod
    def swaps(old: Any, new: Any):
        return diff(old, new)
