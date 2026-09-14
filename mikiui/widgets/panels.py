"""PyQt5/6 & PySide6 style panels and widgets.

Each class maps a Qt widget (QGroupBox, QScrollArea, QMdiArea, ...) onto a
MikiUI component tree, keeping the beginner-friendly constructor style and
accessibility attributes from the framework conventions.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from ..components import (
    H1,
    A,
    Button,
    Div,
    Input,
    Label,
    Legend,
    Li,
    P,
    Progress,
    Span,
    Ul,
)
from ..components.base import Component
from ..components.tabs import Tabs
from ..engine import _
from ..engine.bridge import bridge_attr


class GroupBox(Component):
    """A titled group box (maps ``QGroupBox``).

    :param title: legend text shown at the top of the fieldset.
    :param content: child content placed inside the group.
    """

    tag = "fieldset"

    def __init__(self, title: str, *content: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-groupbox")
        super().__init__(Legend(title), *content, **attrs)


class ScrollPanel(Component):
    """A scrollable panel (maps ``QScrollArea``).

    :param content: child content placed in the scrollable area.
    """

    tag = "div"

    def __init__(self, *content: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-scrollpanel")
        style = attrs.get("style")
        if isinstance(style, dict):
            style.setdefault("overflow", "auto")
        elif isinstance(style, str):
            if "overflow" not in style:
                style = style.rstrip(";") + "; overflow:auto"
            attrs["style"] = style.lstrip(";")
        else:
            attrs["style"] = "overflow:auto"
        super().__init__(*content, **attrs)


class StackedPanel(Component):
    """A stacked widget showing one page at a time (maps ``QStackedWidget``).

    :param pages: a list of ``(title, content)`` pairs.
    :param active: index of the initially-visible page (default 0).
    :param panel_id: optional DOM id for the panel container.
    """

    tag = "div"

    def __init__(
        self,
        pages: list[tuple[str, Any]],
        active: int = 0,
        panel_id: str | None = None,
        **attrs: Any,
    ) -> None:
        if not pages:
            raise ValueError("StackedPanel requires at least one page")
        active = max(0, min(active, len(pages) - 1))

        attrs.setdefault("class_", "miki-stackedpanel")
        attrs.setdefault("role", "group")
        attrs.setdefault("aria_label", _("stackedpanel_label", "Stacked panel"))
        attrs.setdefault("data-miki-stackedpanel", "true")
        if panel_id:
            attrs["id"] = panel_id

        group = "miki-stacked-" + uuid.uuid4().hex[:8]

        buttons = []
        panels = []
        for i, (title, content) in enumerate(pages):
            is_active = i == active
            tab_attrs = {
                "type": "button",
                "role": "tab",
                "id": f"{group}-tab-{i}",
                "aria_selected": "true" if is_active else "false",
                "aria_controls": f"{group}-page-{i}",
                "tabindex": "0" if is_active else "-1",
                "class_": "miki-stack-tab" + (" miki-stack-tab-active" if is_active else ""),
                "data_miki_stack_tab": "true",
                "data_miki_stack_index": str(i),
            }
            buttons.append(Button(title, **tab_attrs))
            panels.append(
                Div(
                    content,
                    role="tabpanel",
                    id=f"{group}-page-{i}",
                    aria_labeledby=f"{group}-tab-{i}",
                    **({"style": "display:none", "aria_hidden": "true"} if not is_active else {}),
                )
            )

        super().__init__(
            Div(*buttons, class_="miki-stack-tabs", role="tablist"),
            Div(*panels, id=f"{group}-pages", class_="miki-stack-pages"),
            **attrs,
        )


class ToolboxPanel(Component):
    """A collapsible toolbox of grouped items (maps ``QToolBox``).

    :param groups: a dict mapping a group title to arbitrary content.
    """

    tag = "div"

    def __init__(self, groups: dict[str, Any], **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-toolbox")
        attrs.setdefault("role", "tablist")
        attrs.setdefault("aria_label", _("toolbox_label", "Toolbox"))
        sections = []
        for i, (title, content) in enumerate(groups.items()):
            section = Div(
                Div(title, class_="miki-toolbox-header", role="tab", aria_selected="false", tabindex="0"),
                Div(content, class_="miki-toolbox-body", role="tabpanel"),
                class_="miki-toolbox-section",
                role="group",
            )
            sections.append(section)
        super().__init__(*sections, **attrs)


class Toolbar(Component):
    """A horizontal toolbar of actions (maps ``QToolBar``).

    :param items: toolbar child content (buttons, actions, ...).
    """

    tag = "div"

    def __init__(self, *items: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-toolbar")
        attrs.setdefault("role", "toolbar")
        attrs.setdefault("aria_label", _("toolbar_label", "Toolbar"))
        super().__init__(*items, **attrs)


class StatusBar(Component):
    """A status bar showing informational items (maps ``QStatusBar``).

    :param items: status child content.
    """

    tag = "footer"

    def __init__(self, *items: Any, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-statusbar")
        attrs.setdefault("role", "status")
        attrs.setdefault("aria_live", "polite")
        super().__init__(*items, **attrs)


class MenuBar(Component):
    """A menu bar with dropdown sub-menus (maps ``QMenuBar``/``QMenu``).

    Each top-level item is a ``(label, sub_items)`` pair.  ``sub_items``
    is a list of action entries.  An action entry may be:

    * ``(label, href)`` — a simple link item.
    * ``(label, href, icon)`` — link item with an optional icon label.
    * ``(label, href, icon, shortcut)`` — link item with icon + shortcut text.
    * ``"divider"`` or ``None`` — a horizontal separator.
    * ``(label, href, icon, shortcut, disabled)`` — disabled item when
      ``disabled`` is truthy.

    Disabled items render with ``aria-disabled`` and are skipped during
    keyboard navigation.

    :param items: list of ``(label, sub_items)`` pairs.
    :param bar_id: optional DOM id for the menu bar.
    """

    tag = "nav"

    def __init__(
        self,
        items: list[tuple[str, list[Any]]],
        bar_id: str | None = None,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-menubar")
        attrs.setdefault("aria_label", _("menubar_label", "Main menu"))
        attrs.setdefault("data-miki-menubar", "true")
        attrs.setdefault("role", "menubar")
        attrs.setdefault("touch-action", "manipulation")
        if bar_id:
            attrs["id"] = bar_id

        menus = []
        for label, sub_items in items:
            action_items: list[Any] = []
            for entry in sub_items:
                if entry is None or entry == "divider":
                    action_items.append(Li(class_="miki-menu-divider", role="separator"))
                    continue

                sub_label = entry[0]
                href = entry[1] if len(entry) > 1 else "#"
                icon = entry[2] if len(entry) > 2 else None
                shortcut = entry[3] if len(entry) > 3 else None
                disabled = bool(entry[4]) if len(entry) > 4 else False

                parts: list[Any] = []
                if icon:
                    parts.append(Span(icon, class_="miki-menu-icon"))
                parts.append(Span(sub_label, class_="miki-menu-label"))
                if shortcut:
                    parts.append(Span(shortcut, class_="miki-menu-shortcut"))

                link_attrs: dict[str, Any] = {
                    "role": "menuitem",
                    "class_": "miki-menu-item",
                    "tabindex": "-1",
                }
                if disabled:
                    link_attrs["aria_disabled"] = "true"
                    link_attrs["class_"] += " miki-menu-item-disabled"
                    link_attrs["tabindex"] = "-1"
                    link = A(*parts, href="javascript:void(0)", **link_attrs)
                else:
                    link = A(*parts, href=href, aria_label=sub_label, **link_attrs)

                action_items.append(Li(link, class_="miki-menu-item-wrap"))

            menus.append(
                Div(
                    Button(
                        label,
                        type="button",
                        class_="miki-menu-title",
                        aria_haspopup="true",
                        aria_expanded="false",
                        aria_label=f"Open {label} menu",
                    ),
                    Ul(
                        *action_items,
                        class_="miki-menu-dropdown",
                        role="menu",
                    ),
                    class_="miki-menu",
                )
            )
        super().__init__(*menus, **attrs)


class SplashScreen(Component):
    """A full-screen splash overlay (maps ``QSplashScreen``).

    :param title: large centered title text.
    :param subtitle: smaller centered subtitle text.
    """

    tag = "div"

    def __init__(self, title: str, subtitle: str = "", **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-splash")
        attrs.setdefault("role", "dialog")
        attrs.setdefault("aria_label", title)
        children = [Div(title, class_="miki-splash-title")]
        if subtitle:
            children.append(Div(subtitle, class_="miki-splash-subtitle"))
        super().__init__(*children, **attrs)


class MessageBox(Component):
    """A modal message box with improved UX and styling.

    Features:
    - Smooth fade-in/out animations
    - Icon indicators based on kind
    - Promise-style button handling (using native JS)
    - Customizable button text

    Parameters
    ----------
    title : str
        Message box heading.
    message : str
        Body message text.
    kind : str
        One of "info", "warning", "error", "success", or "question".
    buttons : list of (text, value) tuples
        Custom button labels and values.
    **attrs : Additional HTML attributes.
    """

    tag = "div"

    def __init__(
        self,
        title: str,
        message: str,
        kind: str = "info",
        buttons: list[tuple[str, str]] | None = None,
        **attrs: Any,
    ) -> None:
        valid_kinds = ("info", "warning", "error", "success", "question")
        if kind not in valid_kinds:
            raise ValueError(f"kind must be one of {valid_kinds}, got {kind!r}")

        attrs.setdefault("class_", f"miki-messagebox miki-messagebox-{kind}")
        attrs.setdefault("role", "alertdialog")
        attrs.setdefault("aria_label", title)
        attrs.setdefault("aria_modal", "true")
        attrs.setdefault("data-miki-messagebox", "true")

        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅",
            "question": "❓",
        }

        icon_html = Span(icons.get(kind, "ℹ️"), class_="miki-messagebox-icon")

        default_buttons = buttons or [("OK", "ok")]
        button_list = []
        for i, (text, value) in enumerate(default_buttons):
            btn_class = "miki-messagebox-btn"
            if i == 0:
                btn_class += " miki-messagebox-btn-primary"
            button_list.append(
                Button(
                    text,
                    type="button",
                    class_=btn_class,
                    role="button",
                    aria_label=f"Button {text}",
                    **{
                        "data-miki-messagebox-close": "true",
                    },
                )
            )

        body = Div(
            Div(icon_html, title, class_="miki-messagebox-title"),
            P(message, class_="miki-messagebox-message"),
            Div(*button_list, class_="miki-messagebox-buttons"),
            class_="miki-messagebox-body",
        )

        super().__init__(body, **attrs)


class ColorPicker(Component):
    """A color input with a label (maps ``QColorDialog``/color edit).

    :param label: label text.
    :param name: form field name.
    :param value: initial color (``#rrggbb``).
    """

    tag = "div"

    def __init__(
        self,
        label: str = "Color",
        name: str = "color",
        value: str = "#000000",
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-colorpicker")
        field_id = "miki-color-" + uuid.uuid4().hex[:8]
        super().__init__(
            Label(label, for_=field_id, class_="miki-colorpicker-label"),
            Input(
                type="color",
                name=name,
                value=value,
                id=field_id,
                class_="miki-colorpicker-input",
            ),
            **attrs,
        )


class DatePicker(Component):
    """A date input with a label (maps ``QDateEdit``).

    :param label: label text.
    :param name: form field name.
    :param value: initial ISO date (``YYYY-MM-DD``) or ``None``.
    """

    tag = "div"

    def __init__(
        self,
        label: str = "Date",
        name: str = "date",
        value: str | None = None,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-datepicker")
        field_id = "miki-date-" + uuid.uuid4().hex[:8]
        input_attrs: dict[str, Any] = {
            "type": "date",
            "name": name,
            "id": field_id,
            "class_": "miki-datepicker-input",
        }
        if value:
            input_attrs["value"] = value
        super().__init__(
            Label(label, for_=field_id, class_="miki-datepicker-label"),
            Input(**input_attrs),
            **attrs,
        )


class ProgressDialog(Component):
    """A modal progress dialog (maps ``QProgressDialog``).

    Auto-initialized by ``miki_ui.js`` — supports ESC-to-close, overlay click,
    and live progress bar updates via ``mikiProgressDialog.setValue()``.

    :param title: dialog heading.
    :param message: descriptive message shown above the progress bar.
    :param value: current progress (0-100).
    :param max: maximum value (default: 100).
    :param closeable: show a close button (useful for non-modal progress).
    """

    tag = "dialog"

    def __init__(
        self,
        title: str = "Please wait",
        message: str = "",
        value: int = 0,
        max: int = 100,
        closeable: bool = False,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-progressdialog miki-dialog miki-dialog-md")
        attrs.setdefault("role", "dialog")
        attrs.setdefault("aria-modal", "true")
        attrs.setdefault("aria-label", title)
        attrs.setdefault("data-miki-progress-dialog", "true")
        attrs.setdefault("data-miki-dialog", "true")
        attrs.setdefault("data-miki-dialog-close-on-overlay", "false")
        attrs.setdefault("data-miki-dialog-close-on-escape", "true")
        attrs.setdefault("data-value", str(value))
        attrs.setdefault("data-max", str(max))

        children: list[Any] = [
            Div(title, class_="miki-progressdialog-title"),
        ]
        if message:
            children.append(P(message, class_="miki-progressdialog-message"))
        children.append(
            Progress(
                value=value,
                max=max,
                variant="striped",
                class_="miki-progressdialog-bar",
            )
        )

        if closeable:
            children.append(
                Button(
                    "×",
                    type="button",
                    class_="miki-dialog-close-btn",
                    role="button",
                    aria_label="Close dialog",
                    **{"data-miki-dialog-close": "true"},
                )
            )

        super().__init__(*children, **attrs)


class LCDNumber(Component):
    """A seven-segment style numeric display (maps ``QLCDNumber``).

    :param value: the number to display.
    :param digits: number of digits to reserve.
    """

    tag = "div"

    def __init__(self, value: int | float = 0, digits: int = 6, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-lcd")
        attrs.setdefault("role", "status")
        attrs.setdefault("aria_label", _("lcd_label", "LCD display"))
        text = f"{value:0{digits}d}" if isinstance(value, int) else str(value)
        super().__init__(Span(text, class_="miki-lcd-value"), **attrs)


class Dial(Component):
    """A circular rotary dial control (maps ``QDial``).

    Renders a single circular track with a visual knob that the user can
    drag around the arc, plus a live numeric value displayed below the dial.
    Supports mouse, touch, and keyboard interaction (arrows, Home/End).
    The knob and value are kept in sync via ``mikiDial`` JS which also
    dispatches ``miki:dial:change`` with the new value and old value.

    :param value: initial value.
    :param min: minimum value.
    :param max: maximum value.
    :param step: step increment for keyboard / fine-tune (default 1).
    :param size: diameter of the dial in pixels (default 140).
    :param wrap: 'hard' = jump from max to min on wrap, 'none' = no wrap
      (default 'none').
    :param on_change: optional Python callback ``Callable[[int, int], None]``
      invoked server-side with ``(value, old_value)`` on change.

    Example::

        from mikiui.widgets import Dial, Span

        def on_dial_change(val, old):
            print(f"Dial: {old} -> {val}")

        Dial(value=50, min=0, max=100, on_change=on_dial_change)

    HTML structure::

        <div class="miki-dial" data-miki-dial="true" ...>
          <div class="miki-dial-track">          <!-- the visible circle -->
            <span class="miki-dial-knob" ...>    <!-- the draggable indicator -->
            <span class="miki-dial-progress">    <!-- conic-gradient fill -->
          </div>
          <div class="miki-dial-display">        <!-- below the circle -->
            <span class="miki-dial-value">50</span>
          </div>
          <input type="range" class="miki-dial-input" ...> <!-- hidden, captures drag -->
        </div>
    """

    tag = "div"

    def __init__(
        self,
        value: int = 0,
        min: int = 0,
        max: int = 100,
        step: int = 1,
        size: int = 140,
        wrap: str = "none",
        on_change: Callable[[int, int], None] | None = None,
        **attrs: Any,
    ) -> None:
        if max <= min:
            raise ValueError(f"max ({max}) must be greater than min ({min})")
        if not (min <= value <= max):
            raise ValueError(f"value ({value}) must be between min ({min}) and max ({max})")
        if wrap not in ("none", "hard"):
            raise ValueError(f"wrap must be 'none' or 'hard', got {wrap!r}")
        if size < 60:
            raise ValueError(f"size ({size}) must be at least 60px")

        attrs.setdefault("class_", "miki-dial")
        attrs.setdefault("role", "group")
        attrs.setdefault("aria-label", _("dial_label", "Dial"))
        attrs.setdefault("data-miki-dial", "true")
        attrs.setdefault("data-min", str(min))
        attrs.setdefault("data-max", str(max))
        attrs.setdefault("data-step", str(step))
        attrs.setdefault("data-size", str(size))
        attrs.setdefault("data-wrap", wrap)

        if on_change is not None:
            self._on_change = on_change

        # Compute initial rotation for the knob (-135 to +135 degrees, 270° arc)
        percent = ((value - min) / (max - min)) * 100
        rotation = (percent / 100) * 270 - 135

        track_style = f"--miki-dial-size: {size}px;"

        super().__init__(
            Div(
                Span(class_="miki-dial-progress"),
                Span(
                    class_="miki-dial-knob",
                    style=f"transform: rotate({rotation}deg);",
                ),
                Input(
                    type="range",
                    min=min,
                    max=max,
                    step=step,
                    value=value,
                    class_="miki-dial-input",
                    **{"aria-label": _("dial_label", "Dial")},
                ),
                class_="miki-dial-track",
                style=track_style,
            ),
            Div(
                Span(str(value), class_="miki-dial-value"),
                class_="miki-dial-display",
            ),
            **attrs,
        )


class MdiSubWindow(Component):
    """A sub-window inside an :class:`MdiArea` (maps ``QMdiSubWindow``).

    :param title: window title bar text.
    :param content: window body content.
    :param icon: optional icon text/label shown before the title.
    :param minimizable: show a minimize button (default True).
    :param maximizable: show a maximize button (default True).
    :param closeable: show a close button (default True).
    :param left: initial left offset in px.
    :param top: initial top offset in px.
    :param width: initial width (px or CSS string).
    :param height: initial height (px or CSS string).
    """

    tag = "section"

    def __init__(
        self,
        title: str,
        *content: Any,
        icon: str | None = None,
        minimizable: bool = True,
        maximizable: bool = True,
        closeable: bool = True,
        left: int = 24,
        top: int = 24,
        width: int | str = 420,
        height: int | str = 280,
        **attrs: Any,
    ) -> None:
        def _css(v: int | str, suffix: str = "px") -> str:
            return f"{v}{suffix}" if isinstance(v, (int, float)) else str(v)

        attrs.setdefault("class_", "miki-mdi-subwindow")
        style_parts = [
            f"left:{_css(left)}",
            f"top:{_css(top)}",
            f"width:{_css(width)}",
            f"height:{_css(height)}",
        ]
        existing_style = attrs.pop("style", "")
        if existing_style and not existing_style.endswith(";"):
            existing_style += ";"
        attrs["style"] = existing_style + ";".join(style_parts)

        title_children: list[Any] = []
        if icon:
            title_children.append(Span(icon, class_="miki-mdi-icon"))
        title_children.append(Span(title, class_="miki-mdi-title"))

        control_buttons: list[Any] = []
        if minimizable:
            control_buttons.append(
                Button(
                    "—",
                    type="button",
                    class_="miki-mdi-minimize",
                    aria_label=_("mdi_minimize", "Minimize window"),
                    **{"data-miki-mdi-minimize": "true"},
                )
            )
        if maximizable:
            control_buttons.append(
                Button(
                    "▢",
                    type="button",
                    class_="miki-mdi-maximize",
                    aria_label=_("mdi_maximize", "Maximize window"),
                    **{"data-miki-mdi-maximize": "true"},
                )
            )
        if closeable:
            control_buttons.append(
                Button(
                    "×",
                    type="button",
                    class_="miki-mdi-close",
                    aria_label=_("mdi_close", "Close window"),
                    **{"data-miki-mdi-close": "true"},
                )
            )

        title_bar = Div(
            Div(*title_children, class_="miki-mdi-title-group"),
            Div(*control_buttons, class_="miki-mdi-controls"),
            class_="miki-mdi-titlebar",
        )
        body = Div(*content, class_="miki-mdi-body")
        super().__init__(title_bar, body, **attrs)


class MdiArea(Component):
    """A multiple-document interface area (maps ``QMdiArea``).

    :param windows: :class:`MdiSubWindow` instances placed in the area.
    :param area_id: optional DOM id for the MDI area.
    """

    tag = "div"

    def __init__(self, *windows: Any, area_id: str | None = None, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-mdiarea")
        attrs.setdefault("role", "group")
        attrs.setdefault("aria_label", _("mdi_label", "Workspace"))
        attrs.setdefault("data-miki-mdiarea", "true")
        if area_id:
            attrs["id"] = area_id
        super().__init__(*windows, **attrs)


class CollapsiblePanel(Component):
    """A collapsible panel with smooth animations and accessibility.

    Uses native DOM events for expand/collapse with smooth transitions.

    Parameters
    ----------
    title : str
        Summary text shown in the header.
    *content : Any
        Content to hide/show.
    open : bool
        Whether the panel starts expanded.
    animate : bool
        Enable smooth height transition animation.
    icon : str | None
        Optional icon to show in the header.
    **attrs : Additional HTML attributes.
    """

    tag = "div"

    def __init__(
        self,
        title: str,
        *content: Any,
        open: bool = False,
        animate: bool = True,
        icon: str | None = None,
        **attrs: Any,
    ) -> None:
        state = "open" if open else "closed"
        attrs.setdefault("class_", f"miki-collapsible miki-collapsible-{state}")
        attrs.setdefault("role", "group")
        attrs.setdefault("aria-label", f"{title} panel")
        attrs.setdefault("data-miki-collapsible", "true")
        attrs.setdefault("data-miki-state", state)

        summary_children: list[Any] = []
        if icon:
            summary_children.append(Span(icon, class_="miki-collapsible-icon"))
        summary_children.append(Span(title, class_="miki-collapsible-summary"))

        if animate:
            body_class = "miki-collapsible-body miki-collapsible-body-animated"
        else:
            body_class = "miki-collapsible-body"

        summary_inner = Div(*summary_children, class_="miki-collapsible-summary-inner")
        summary = Div(
            summary_inner,
            Span("▼" if open else "▶", class_="miki-collapsible-toggle"),
            class_="miki-collapsible-header miki-collapsible-summary-clickable",
            role="button",
            tabindex="0",
            aria_expanded=str(open).lower(),
            **{"data-miki-collapsible-header": "true"},
        )

        body = Div(*content, class_=body_class)

        super().__init__(summary, body, **attrs)


class SidePanel(Component):
    """A fixed side panel with improved styling and accessibility.

    Parameters
    ----------
    side : str
        "left" or "right".
    *content : Any
        Panel body content.
    collapsible : bool
        Allow collapsing via overlay toggle.
    header : str | None
        Optional header title.
    **attrs : Additional HTML attributes.
    """

    tag = "aside"

    def __init__(
        self,
        side: str = "left",
        *content: Any,
        collapsible: bool = False,
        header: str | None = None,
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        if side not in ("left", "right"):
            raise ValueError(f"side must be 'left' or 'right', got {side!r}")

        classes = f"miki-sidepanel miki-side-{side}"
        if class_:
            classes += f" {class_}"
        if collapsible:
            classes += " miki-side-collapsible"

        attrs.setdefault("class_", classes)
        attrs.setdefault("aria_label", f"Side panel ({side})")
        attrs.setdefault("role", "complementary")

        children: list[Any] = []

        if header:
            header_children: list[Any] = [H1(header, class_="miki-sidepanel-title")]
            if collapsible:
                header_children.append(
                    Button(
                        "×",
                        type="button",
                        class_="miki-sidepanel-close",
                        aria_label="Close panel",
                        **bridge_attr("click", "this.closest('.miki-sidepanel').style.display='none';"),
                    )
                )
            children.append(Div(*header_children, class_="miki-sidepanel-header"))

        children.extend(content)

        super().__init__(*children, **attrs)


class LogViewer(Component):
    """A monospace log viewer with severity coloring (maps a log widget).

    Parameters
    ----------
    lines : list | None
        A list of log entries. Each entry may be a string (treated as "info")
        or a ``(level, message)`` tuple.
    auto_scroll : bool
        Auto-scroll to bottom when new lines added.
    line_numbers : bool
        Show line numbers.
    **attrs : Additional HTML attributes.
    """

    tag = "div"

    def __init__(
        self,
        lines: list[Any] | None = None,
        auto_scroll: bool = True,
        line_numbers: bool = False,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-logviewer")
        attrs.setdefault("role", "log")
        attrs.setdefault("aria_live", "polite")

        children = []
        for line_num, entry in enumerate(lines or [], start=1):
            if isinstance(entry, (tuple, list)) and len(entry) == 2:
                level, message = entry
            else:
                level, message = "info", entry

            line_attrs = {"class_": f"miki-log-line miki-log-{level}"}
            if line_numbers:
                line_attrs["class_"] += " miki-log-line-numbered"

            if line_numbers:
                children.append(
                    Div(
                        Span(f"{line_num:4d}", class_="miki-log-line-num"),
                        Span(str(message), class_="miki-log-line-content"),
                        **line_attrs,
                    )
                )
            else:
                children.append(Div(str(message), **line_attrs))

        super().__init__(*children, **attrs)


class TabbedPanel(Tabs):
    """A tabbed panel (maps ``QTabWidget``).

    Reuses the offline-friendly switching logic of :class:`Tabs` but with a
    distinct ``miki-tabbedpanel`` class.

    Features:
    - Keyboard navigation between tabs
    - Closeable tabs (optional)
    - Icon support

    Parameters
    ----------
    tabs : list
        A list of ``(label, content)`` pairs.
    closable : bool
        Show close button on each tab.
    **attrs : Additional HTML attributes.
    """

    def __init__(
        self,
        tabs: list[tuple[str, Any] | tuple[str, Any, str]],
        closable: bool = False,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-tabbedpanel")
        super().__init__(tabs, closeable=closable, **attrs)


class ProfilerPanel(Component):
    """A simple profiler panel showing performance metrics.

    Renders a list of ``(label, value)`` pairs in a styled panel.

    Parameters
    ----------
    metrics : list
        A list of ``(label, value)`` pairs.
    **attrs : Additional HTML attributes.
    """

    tag = "div"

    def __init__(self, metrics: list[tuple[str, Any]], **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-profiler")
        attrs.setdefault("role", "region")
        attrs.setdefault("aria_label", _("profiler_label", "Profiler"))
        rows = []
        for label, value in metrics:
            rows.append(
                Div(
                    Span(label, class_="miki-profiler-label"),
                    Span(str(value), class_="miki-profiler-value"),
                    class_="miki-profiler-row",
                )
            )
        super().__init__(
            Div(*rows, class_="miki-profiler-body"),
            **attrs,
        )


class FilePicker(Component):
    """A drag-drop file picker zone.

    Renders a dashed dropzone area with a hidden file input.

    Parameters
    ----------
    name : str
        Form field name for the file input.
    accept : str
        Accepted file types (e.g. "image/*" or ".pdf,.doc").
    multiple : bool
        Allow multiple file selection.
    label : str
        Text shown inside the dropzone.
    **attrs : Additional HTML attributes.
    """

    tag = "div"

    def __init__(
        self,
        name: str = "file",
        accept: str = "*",
        multiple: bool = False,
        label: str = "Drop files here or click to browse",
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-dropzone")
        attrs.setdefault("role", "button")
        attrs.setdefault("tabindex", "0")
        attrs.setdefault("data-miki-dropzone", "true")
        attrs.setdefault("aria-label", "File picker dropzone")

        input_id = f"miki-file-{name}"

        file_input = Input(
            type="file",
            name=name,
            id=input_id,
            accept=accept,
            multiple=multiple,
            class_="miki-file-input",
            **{"data-miki-file-input": "true"},
        )

        label_span = Span(label, class_="miki-dropzone-label")

        super().__init__(file_input, label_span, **attrs)


class MikiMenu(Component):
    """A simple menu of items (maps ``QMenu``).

    :param items: a list of item labels.
    """

    tag = "ul"

    def __init__(self, items: list[str], **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-simple-menu")
        attrs.setdefault("role", "menu")
        attrs.setdefault("aria_label", _("menu_label", "Menu"))
        children = [Div(item, class_="miki-simple-menu-item", role="menuitem") for item in items]
        super().__init__(*children, **attrs)


class MikiSizeGrip(Component):
    """A resize grip handle (maps ``QSizeGrip``).

    Renders a small square grip in the bottom-right corner of its container.
    """

    tag = "div"

    def __init__(self, **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-sizegrip")
        attrs.setdefault("role", "separator")
        attrs.setdefault("aria_label", _("sizegrip_label", "Resize grip"))
        super().__init__(**attrs)


class MikiColumnView(Component):
    """A multi-column browser view (maps ``QColumnView``).

    :param columns: a list of columns, where each column is a list of item labels.
    """

    tag = "div"

    def __init__(self, columns: list[list[str]], **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-columnview")
        attrs.setdefault("role", "list")
        attrs.setdefault("aria_label", _("columnview_label", "Column view"))
        col_divs = [
            Div(
                *[Div(item, class_="miki-column-item", role="listitem") for item in col],
                class_="miki-column",
                role="group",
            )
            for col in columns
        ]
        super().__init__(*col_divs, **attrs)


class MikiButtonGroup(Component):
    """A group of buttons (maps ``QButtonGroup``).

    :param buttons: a list of button labels.
    """

    tag = "div"

    def __init__(self, buttons: list[str], **attrs: Any) -> None:
        attrs.setdefault("class_", "miki-btngroup")
        attrs.setdefault("role", "group")
        attrs.setdefault("aria_label", _("btngroup_label", "Button group"))
        children = [Div(label, class_="miki-btn", role="button") for label in buttons]
        super().__init__(*children, **attrs)
