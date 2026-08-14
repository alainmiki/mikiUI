"""Chart component (inline SVG line/bar/pie charts)."""

from __future__ import annotations

import math
from typing import Any

from .base import Component
from .html import Div, Svg


class Chart(Component):
    """A lightweight inline-SVG chart.

    ``kind`` is ``"line"``, ``"bar"``, or ``"pie"``. ``series`` is a list of
    numeric values.  ``width`` and ``height`` control the SVG viewport.
    Pass ``class_`` for additional CSS classes.
    """

    tag = "div"

    def __init__(
        self,
        series: list[float],
        kind: str = "bar",
        width: int = 320,
        height: int = 160,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("role", "img")
        user_class = attrs.pop("class_", "")
        attrs["class_"] = f"miki-chart {user_class}".strip()
        if not series:
            super().__init__(Div("(no data)", class_="miki-chart-empty"), **attrs)
            return
        if kind == "bar":
            svg = self._bars(series, width, height)
        elif kind == "line":
            svg = self._line(series, width, height)
        else:
            svg = self._pie(series, width, height)
        super().__init__(svg, **attrs)

    @staticmethod
    def _bars(series: list[float], w: int, h: int) -> Svg:
        n = len(series)
        gap = 4
        bw = max(1, (w - gap * (n + 1)) / n)
        maxv = max(series) or 1
        rects = []
        for i, v in enumerate(series):
            x = gap + i * (bw + gap)
            bh = (v / maxv) * (h - 10)
            rects.append(f'<rect x="{x:.1f}" y="{h - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" class="miki-chart-bar"></rect>')
        return Svg("".join(rects), viewBox=f"0 0 {w} {h}", width=w, height=h)

    @staticmethod
    def _line(series: list[float], w: int, h: int) -> Svg:
        n = len(series)
        maxv = max(series) or 1
        pts = []
        for i, v in enumerate(series):
            x = (i / max(1, n - 1)) * w
            y = h - (v / maxv) * (h - 10)
            pts.append(f"{x:.1f},{y:.1f}")
        return Svg(
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="currentColor" class="miki-chart-line"></polyline>',
            viewBox=f"0 0 {w} {h}",
            width=w,
            height=h,
        )

    @staticmethod
    def _pie(series: list[float], w: int, h: int) -> Svg:
        total = sum(series) or 1
        cx, cy, r = w / 2, h / 2, min(w, h) / 2 - 2
        paths = []
        angle = 0.0
        for i, v in enumerate(series):
            frac = v / total
            a2 = angle + frac * 360
            x1 = cx + r * math.cos(math.radians(angle))
            y1 = cy + r * math.sin(math.radians(angle))
            x2 = cx + r * math.cos(math.radians(a2))
            y2 = cy + r * math.sin(math.radians(a2))
            large = 1 if frac > 0.5 else 0
            paths.append(
                f'<path d="M{cx:.1f},{cy:.1f} L{x1:.1f},{y1:.1f} A{r:.1f},{r:.1f} 0 {large} 1 {x2:.1f},{y2:.1f} Z" class="miki-chart-slice"></path>'
            )
            angle = a2
        return Svg("".join(paths), viewBox=f"0 0 {w} {h}", width=w, height=h)
