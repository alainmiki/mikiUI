"""PyQt5/6 & PySide6 style panels and widgets.

Each class maps a Qt widget (QGroupBox, QScrollArea, QMdiArea, ...) onto a
MikiUI component tree, keeping the beginner-friendly constructor style and
accessibility attributes from the framework conventions.
"""

from __future__ import annotations

import uuid
from typing import Any

from ..components import (
    H1,
    A,
    Button,
    Details,
    Div,
    Input,
    Label,
    Legend,
    Li,
    P,
    Progress,
    Span,
    Summary,
    Ul,
)
from ..components.base import Component
from ..components.tabs import Tabs
from ..engine import _


class GroupBox(Component):
    """A titled group box (maps ``QGroupBox``).

    :param title: legend text shown at the top of the fieldset.
    :param content: child content placed inside the group.
    """

    tag = "fieldset"

    def __init__(self, title: str, *content: Any, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-groupbox")
        super().__init__(Legend(title), *content, **attrs)


class ScrollPanel(Component):
    """A scrollable panel (maps ``QScrollArea``).

    :param content: child content placed in the scrollable area.
    """

    tag = "div"

    def __init__(self, *content: Any, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-scrollpanel")
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
    """

    tag = "div"

    def __init__(self, pages: list[tuple[str, Any]], **attrs: Any) -> None:
        attrs.setdefault("class", "miki-stackedpanel")
        group = "miki-stacked-" + uuid.uuid4().hex[:8]

        buttons = []
        panels = []
        for i, (title, content) in enumerate(pages):
            buttons.append(
                Button(
                    title,
                    type="button",
                    role="tab",
                    aria_selected="true" if i == 0 else "false",
                    class_="miki-stack-tab" + (" miki-stack-tab-active" if i == 0 else ""),
                    onclick=(
                        "var ps=document.getElementById('" + group + "-pages').children;"
                        "for(var i=0;i<ps.length;i++){"
                        "ps[i].style.display=(i===" + str(i) + ")?'block':'none';"
                        "this.parentNode.children[i].setAttribute('aria-selected',i===" + str(i) + ");}"
                    ),
                )
            )
            panels.append(
                Div(
                    content,
                    role="tabpanel",
                    id=f"{group}-page-{i}",
                    **({"style": "display:none"} if i != 0 else {}),
                )
            )

        super().__init__(
            Div(*buttons, class_="miki-stack-tabs", role="tablist"),
            Div(*panels, id=f"{group}-pages", class_="miki-stack-pages"),
            **attrs,
        )


class ToolboxPanel(Component):
    """A collapsible toolbox of grouped items (maps ``QToolBox``).

    :param groups: a dict mapping a group title to a list of item contents.
    """

    tag = "div"

    def __init__(self, groups: dict[str, list[Any]], **attrs: Any) -> None:
        attrs.setdefault("class", "miki-toolbox")
        blocks = []
        for title, items in groups.items():
            blocks.append(
                Details(
                    Summary(title, class_="miki-toolbox-summary"),
                    Ul(*[Li(item) for item in items], class_="miki-toolbox-items"),
                    class_="miki-toolbox-group",
                )
            )
        super().__init__(*blocks, **attrs)


class Toolbar(Component):
    """A horizontal toolbar of actions (maps ``QToolBar``).

    :param items: toolbar child content (buttons, actions, ...).
    """

    tag = "div"

    def __init__(self, *items: Any, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-toolbar")
        attrs.setdefault("role", "toolbar")
        attrs.setdefault("aria_label", _("toolbar_label", "Toolbar"))
        super().__init__(*items, **attrs)


class StatusBar(Component):
    """A status bar showing informational items (maps ``QStatusBar``).

    :param items: status child content.
    """

    tag = "footer"

    def __init__(self, *items: Any, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-statusbar")
        attrs.setdefault("role", "status")
        attrs.setdefault("aria_live", "polite")
        super().__init__(*items, **attrs)


class MenuBar(Component):
    """A menu bar with dropdown sub-menus (maps ``QMenuBar``/``QMenu``).

    :param items: a list of ``(label, sub_items)`` pairs where ``sub_items`` is a
        list of ``(label, href)`` pairs.
    """

    tag = "nav"

    def __init__(self, items: list[tuple[str, list[tuple[str, str]]]], **attrs: Any) -> None:
        attrs.setdefault("class", "miki-menubar")
        attrs.setdefault("aria_label", _("menubar_label", "Main menu"))
        menus = []
        for label, sub_items in items:
            menus.append(
                Div(
                    Button(
                        label,
                        type="button",
                        class_="miki-menu-title",
                        aria_haspopup="true",
                    ),
                    Ul(
                        *[Li(A(sub_label, href=href), class_="miki-menu-item") for sub_label, href in sub_items],
                        class_="miki-menu-dropdown",
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
        attrs.setdefault("class", "miki-splash")
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

        attrs.setdefault("class", f"miki-messagebox miki-messagebox-{kind}")
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
                        "onclick": "mikiMessageBox.close(this.closest('.miki-messagebox'));",
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
        attrs.setdefault("class", "miki-colorpicker")
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
        attrs.setdefault("class", "miki-datepicker")
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
        attrs.setdefault("class", "miki-progressdialog miki-dialog miki-dialog-md")
        attrs.setdefault("role", "dialog")
        attrs.setdefault("aria-modal", "true")
        attrs.setdefault("aria-label", title)
        attrs.setdefault("data-miki-progress-dialog", "true")
        attrs.setdefault("data-miki-dialog", "true")
        attrs.setdefault("data-miki-dialog-close-on-overlay", "false")
        attrs.setdefault("data-miki-dialog-close-on-escape", "true")
        attrs.setdefault("data-value", str(value))
        attrs.setdefault("data-max", str(max))

        children = [
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
        attrs.setdefault("class", "miki-lcd")
        attrs.setdefault("role", "status")
        attrs.setdefault("aria_label", _("lcd_label", "LCD display"))
        text = f"{value:0{digits}d}" if isinstance(value, int) else str(value)
        super().__init__(Span(text, class_="miki-lcd-value"), **attrs)


class Dial(Component):
    """A circular dial control (maps ``QDial``).

    Renders a styled range input acting as the dial value, with a visual
    rotary knob and live value display.  ``miki_ui.js`` keeps the knob and
    value in sync and adds keyboard support (arrows, Home/End).

    :param value: initial value.
    :param min: minimum value.
    :param max: maximum value.
    """

    tag = "div"

    def __init__(
        self,
        value: int = 0,
        min: int = 0,
        max: int = 100,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class", "miki-dial")
        attrs.setdefault("role", "group")
        attrs.setdefault("aria-label", _("dial_label", "Dial"))
        attrs.setdefault("data-miki-dial", "true")

        # Compute initial rotation for the knob (0 to 270 degrees)
        percent = ((value - min) / (max - min)) * 100 if max > min else 0
        rotation = (percent / 100) * 270 - 135

        super().__init__(
            Input(
                type="range",
                min=min,
                max=max,
                value=value,
                class_="miki-dial-input",
                **{"aria-label": _("dial_label", "Dial")},
            ),
            Div(
                Span(class_="miki-dial-knob", style=f"transform: rotate({rotation}deg)"),
                class_="miki-dial-track",
            ),
            Div(
                Span("●", class_="miki-dial-thumb"),
                Span(str(value), class_="miki-dial-value"),
                class_="miki-dial-display",
            ),
            **attrs,
        )


class MdiSubWindow(Component):
    """A sub-window inside an :class:`MdiArea` (maps ``QMdiSubWindow``).

    :param title: window title bar text.
    :param content: window body content.
    """

    tag = "section"

    def __init__(self, title: str, *content: Any, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-mdi-subwindow")
        title_bar = Div(
            Span(title, class_="miki-mdi-title"),
            Button(
                "×",
                type="button",
                class_="miki-mdi-close",
                aria_label=_("mdi_close", "Close window"),
                onclick="var w=this.closest('.miki-mdi-subwindow'); if(w) w.style.display='none';",
                **{"data-miki-mdi-close": "true"},
            ),
            class_="miki-mdi-titlebar",
        )
        body = Div(*content, class_="miki-mdi-body")
        super().__init__(title_bar, body, **attrs)


class MdiArea(Component):
    """A multiple-document interface area (maps ``QMdiArea``).

    :param windows: :class:`MdiSubWindow` instances placed in the area.
    """

    tag = "div"

    def __init__(self, *windows: Any, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-mdiarea")
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

        attrs.setdefault("class", classes)
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
                        onclick="this.closest('.miki-sidepanel').style.display='none';",
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
        attrs.setdefault("class", "miki-logviewer")
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

    def __init__(self, tabs: list[tuple[str, Any]], closable: bool = False, **attrs: Any) -> None:
        attrs.setdefault("class", "miki-tabbedpanel")
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
        attrs.setdefault("class", "miki-profiler")
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
        attrs.setdefault("class", "miki-dropzone")
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
