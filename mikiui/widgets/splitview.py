"""Resizable SplitView widget with draggable splitter.

The splitter allows users to resize panes by dragging.
Uses direct DOM manipulation for the drag-to-resize behavior.

For advanced customization, pass additional CSS classes or attributes.

Example::

    SplitView(
        Div("Left Pane", class_="p-4"),
        Div("Right Pane", class_="p-4"),
    )

    # Vertical split
    SplitView(Div("Top"), Div("Bottom"), orientation="vertical")
"""

from __future__ import annotations

from typing import Any

from ..components import Div
from ..components.base import Component


class SplitView(Component):
    """A split view with draggable splitter.

    :param left: content for the first (left/top) pane.
    :param right: content for the second (right/bottom) pane.
    :param orientation: ``"horizontal"`` (side-by-side, default) or ``"vertical"``.
    :param attrs: Additional HTML attributes.

    Usage::

        # Horizontal split (side by side)
        SplitView(Div("Left"), Div("Right"))

        # Vertical split (stacked)
        SplitView(Div("Top"), Div("Bottom"), orientation="vertical")

    For proper sizing, wrap in a container with defined dimensions (e.g., using
    Tailwind's h-screen class or setting a specific height).
    """

    tag = "div"

    def __init__(
        self,
        left: Any,
        right: Any,
        orientation: str = "horizontal",
        **attrs: Any,
    ) -> None:
        is_horizontal = orientation == "horizontal"

        attrs.setdefault("class", "miki-splitview")
        attrs.setdefault("x_data", "{dragging:false}")

        container_style = "display:flex;flex-direction:row gap:0.5rem;height:100%;" if is_horizontal else "display:flex;flex-direction:column gap:0.5rem;height:100%;"
        attrs.setdefault("style", container_style)

        pane_style = "flex:1;overflow:auto;min-width:150px;min-height:0"

        left_pane = Div(left, class_="miki-split-pane miki-split-left", style=pane_style)
        right_pane = Div(right, class_="miki-split-pane miki-split-right", style=pane_style)

        splitter_js = """
            const el = this;
            const startLen = el.pageX || el.clientX;
            const startWidth = parseInt(el.previousElementSibling.style.width || '200');
            const viewportW = Math.max(document.documentElement.clientWidth, window.innerWidth);
            const minW = 150;
            const maxW = viewportW - minW - 10;
            const mv = (e) => {
                const diff = (e.pageX || e.clientX) - startLen;
                const newW = Math.max(minW, Math.min(maxW, startWidth + diff));
                el.previousElementSibling.style.width = newW + 'px';
                el.previousElementSibling.style.flex = '0 0 ' + newW + 'px';
                el.nextElementSibling.style.flex = '1';
            };
            const mu = () => { document.removeEventListener('mousemove', mv); document.removeEventListener('mouseup', mu); };
            document.addEventListener('mousemove', mv);
            document.addEventListener('mouseup', mu);
        """

        splitter = Div(
            "",
            class_="miki-splitter",
            style="user-select:none;touch-action:none;",
            onmousedown=splitter_js,
            role="separator",
            aria_orientation="horizontal" if is_horizontal else "vertical",
        )

        super().__init__(left_pane, splitter, right_pane, **attrs)