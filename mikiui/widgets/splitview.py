"""Modern SplitView widget - inspired by VS Code, Material Design, and d3.js.

Design Principles (from VS Code, IntelliJ, three.js):
- Mouse cursor changes on hover (ew-resize, ns-resize, nwse-resize)
- Blue hover accent on the sash/splitter
- Visual gripper dots (● ● ●) matching the active resize axis
- Double-click to maximize/restore the first pane
- Keyboard arrow keys for fine adjustment (5px, Shift+arrow = 1px)
- Touch support with single-finger drag
- Nested SplitView support (splitviews inside splitviews work automatically)
- Dynamic add/remove panes via JavaScript API
- Save/load layout state as JSON

Example::

    from mikiui.widgets import SplitView
    from mikiui.components import Div

    # Standard split view (drag splitter left/right to resize panes)
    SplitView(
        Div("Left"),
        Div("Right"),
        orientation="horizontal",
        min_size=200,
    )

    # Vertical split (drag splitter up/down to resize panes)
    SplitView(
        Div("Top"),
        Div("Bottom"),
        orientation="vertical",
        resize_mode="vertical",
    )

    # Bidirectional split — drag in any direction
    # The first meaningful drag direction locks the axis
    SplitView(
        Div("A"),
        Div("B"),
        resize_mode="both",
    )

    # Nested SplitView
    SplitView(
        Div("Left",
            SplitView(Div("Top-Left"), Div("Bottom-Left"), orientation="vertical"),
        ),
        Div("Right"),
    )
"""

from __future__ import annotations

from typing import Any

from ..components import Div
from ..components.base import Component


class SplitView(Component):
    """A sophisticated split view with dynamic, directional resizing.

    Inspired by:
    - VS Code's editor groups (drag to resize, double-click to maximize)
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
        'horizontal' for side-by-side (drag splitter left/right),
        'vertical' for stacked (drag splitter up/down).
    min_size : int
        Minimum pixel size for each pane (default: 50).
    separator_width : int
        Visual separator thickness in pixels (default: 8).
    resize_mode : str
        Controls which directions the splitter responds to:
        - 'horizontal' (default): Drag left/right to resize panes.
        - 'vertical': Drag up/down to resize panes.
        - 'both': Drag in any direction; the first meaningful movement
          locks the active axis to prevent jitter.
    collapsible : bool
        Whether panes can be collapsed (default: True).
    hover_class : str
        CSS class applied on hover (default: ring accent).
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
        min_size: int = 50,
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

        attrs.setdefault(
            "class_", f"miki-splitview miki-splitview-{orientation}-{str(id(self))[:6]}"
        )
        attrs.setdefault("role", "group")
        attrs.setdefault("data-miki-splitview", "true")
        attrs.setdefault("data-orientation", orientation)
        attrs.setdefault("data-min-size", str(min_size))
        attrs.setdefault("data-resize-mode", resize_mode)
        attrs.setdefault("style", "")
        attrs["style"] += f"--miki-splitter-width: {separator_width}px;"

        container_class = "miki-splitview-container"
        if is_horizontal:
            container_class += " miki-split-h"
        else:
            container_class += " miki-split-v"

        attrs["class_"] = attrs.get("class_", "") + " " + container_class

        # Pane sizing: use min_size for the relevant axis
        first_style = (
            "overflow:auto;"
            + (f"min-width:{min_size}px;" if is_horizontal else f"min-height:{min_size}px;")
        )
        second_style = (
            "overflow:auto;"
            + (f"min-width:{min_size}px;" if is_horizontal else f"min-height:{min_size}px;")
        )

        first_attrs = {
            "class_": "miki-split-pane miki-split-first",
            "style": first_style,
            "role": "region",
            "data-miki-split-pane": "first",
        }

        second_attrs = {
            "class_": "miki-split-pane miki-split-second",
            "style": second_style,
            "role": "region",
            "data-miki-split-pane": "second",
        }

        first_pane = Div(left, **first_attrs)
        second_pane = Div(right, **second_attrs)

        splitter = Div(
            "",
            class_=f"miki-splitter miki-splitter-clickable {hover_class}",
            role="separator",
            aria_orientation="horizontal" if is_horizontal else "vertical",
            tabindex="0",
            **{"data-miki-splitter": "true", "data-splitter-width": str(separator_width)},
        )

        super().__init__(first_pane, splitter, second_pane, **attrs)
