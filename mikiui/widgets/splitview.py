"""Modern SplitView widget - inspired by VS Code, Material Design, and d3.js.

Design Principles (from VS Code, IntelliJ, three.js):
- Mouse cursor changes on hover (ew-resize, ns-resize)
- Visual feedback during drag (outline, opacity change)
- Double-click to maximize/restore
- Keyboard arrow keys for fine adjustment
- Touch support with pinch-to-resize

Example::

    # Standard split view (drag splitter left/right to resize panes)
    SplitView(
        CodeEditor(content="print('hello')"),
        OutputPanel(lines=["Hello, world!"]),
        separator_width=8,
        min_size=200,
    )

    # Vertical split (drag splitter up/down to resize panes)
    SplitView(
        TopPane(),
        BottomPane(),
        resize_mode="vertical",
    )

    # Bidirectional split — drag in any direction
    SplitView(
        TopLeftPane(),
        TopRightPane(),
        resize_mode="both",
    )
"""

from __future__ import annotations

from typing import Any

from ..components import Div
from ..components.base import Component


class SplitView(Component):
    """A sophisticated split view with dynamic, directional resizing.

    Inspired by:
    - VS Code's editor groups (drag tab to dock)
    - IntelliJ's tool windows (double-click to collapse)
    - d3.js drag behavior (touch + mouse support)
    - Material Design dividers (visual feedback)

    Parameters
    ----------
    left : Any
        Content for the first pane.
    right : Any
        Content for the second pane.
    orientation : str
        'horizontal' for side-by-side (splitter resizes in X axis),
        'vertical' for stacked (splitter resizes in Y axis).
    min_size : int
        Minimum pixel size for each pane.
    separator_width : int
        Visual separator thickness.
    resize_mode : str
        Controls which directions the splitter responds to:
        - 'horizontal' (default): Drag left/right to resize panes.
        - 'vertical': Drag up/down to resize panes.
        - 'both': Drag in any direction (all 4 sides) to resize panes.
    collapsible : bool
        Whether panes can be collapsed to separator.
    **attrs : Additional HTML attributes.

    Example
    -------
    >>> sv = SplitView(Div("Left"), Div("Right"))
    >>> sv = SplitView(Div("Top"), Div("Bottom"), resize_mode="vertical")
    >>> sv = SplitView(Div("A"), Div("B"), resize_mode="both")
    """

    tag = "div"

    def __init__(
        self,
        left: Any,
        right: Any,
        orientation: str = "horizontal",
        min_size: int = 200,
        separator_width: int = 8,
        resize_mode: str = "horizontal",
        collapsible: bool = True,
        hover_class: str = "hover:ring-2 hover:ring-offset-2 hover:ring-accent",
        **attrs: Any,
    ) -> None:
        is_horizontal = orientation == "horizontal"

        valid_resize_modes = ("horizontal", "vertical", "both")
        if resize_mode not in valid_resize_modes:
            raise ValueError(
                f"resize_mode must be one of {valid_resize_modes}, got {resize_mode!r}"
            )

        attrs.setdefault("class", f"miki-splitview miki-splitview-{orientation}-{str(id(self))[:6]}")
        attrs.setdefault("role", "group")
        attrs.setdefault("data-miki-splitview", "true")
        attrs.setdefault("data-orientation", orientation)
        attrs.setdefault("data-min-size", str(min_size))
        attrs.setdefault("data-resize-mode", resize_mode)

        container_class = "miki-splitview-container"
        if is_horizontal:
            container_class += " miki-split-h"
        else:
            container_class += " miki-split-v"

        attrs.setdefault("class", attrs.get("class", "") + " " + container_class)

        first_attrs = {
            "class_": "miki-split-pane miki-split-first",
            "style": f"overflow:auto;min-width:{min_size};min-height:0",
            "role": "region",
            "data-miki-split-pane": "first",
        }

        second_attrs = {
            "class_": "miki-split-pane miki-split-second",
            "style": f"overflow:auto;min-width:{min_size};min-height:0",
            "role": "region",
            "data-miki-split-pane": "second",
        }

        first_pane = Div(left, **first_attrs)
        second_pane = Div(right, **second_attrs)

        splitter = Div(
            "",
            class_="miki-splitter miki-splitter-clickable",
            role="separator",
            aria_orientation="horizontal" if is_horizontal else "vertical",
            tabindex="0",
            **{"data-miki-splitter": "true"},
        )

        super().__init__(first_pane, splitter, second_pane, **attrs)
