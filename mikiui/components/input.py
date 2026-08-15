"""Input components with enhanced styling and accessibility.

Features:
- Multiple variants (default, filled, outlined)
- Sizes (sm, md, lg)
- Validation states (valid, invalid, warning)
- Loading states
- Icon support
- Dark mode compatible
- Full ARIA support

Input types supported:
- text, password, email, number, tel, url, search, date, datetime-local,
- month, week, time, color, range, file, checkbox, radio, toggle, switch
"""

from __future__ import annotations

from typing import Any

from .base import Component


class Input(Component):
    """A styled ``<input>`` element with modern look.

    Parameters
    ----------
    *children : Content (usually empty for inputs)
    variant : str
        "default" (outlined), "filled" (filled background), or "text" (text-style).
    size : str
        "sm", "md" (default), or "lg".
    state : str
        "default" (default), "valid", "invalid", or "warning".
    loading : bool
        Show loading spinner.
    disabled : bool
        Disable the input.
    **attrs : Additional HTML attributes.

    Example
    -------
    >>> Input("Email", type="email", placeholder="you@example.com", variant="filled")
    >>> Input(type="password", loading=True)
    >>> Input("Username", type="text", state="valid")
    """

    tag = "input"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        variant = attrs.pop("variant", "default")
        size = attrs.pop("size", "md")
        state = attrs.pop("state", "default")
        loading = attrs.pop("loading", False)
        disabled = attrs.pop("disabled", False)

        classes = self._build_classes(variant, size, state, loading, disabled)
        user_classes = attrs.pop("class_", "")
        attrs["class_"] = f"{classes} {user_classes}".strip()

        if loading:
            attrs["aria-busy"] = "true"
        if disabled:
            attrs["aria-disabled"] = "true"

        super().__init__(*children, **attrs)

    @classmethod
    def _build_classes(cls, variant: str, size: str, state: str, loading: bool, disabled: bool) -> str:
        base = "miki-input"

        if variant == "filled":
            base += " miki-input-filled"
        elif variant == "text":
            base += " miki-input-text"

        if size == "sm":
            base += " miki-input-sm"
        elif size == "lg":
            base += " miki-input-lg"

        if state == "valid":
            base += " miki-input-valid"
        elif state == "invalid":
            base += " miki-input-invalid"
        elif state == "warning":
            base += " miki-input-warning"

        if loading:
            base += " miki-input-loading"
        if disabled:
            base += " miki-input-disabled"

        return base

    @staticmethod
    def color(label: str, name: str = "color", value: str = "#000000", **attrs: Any) -> Any:
        """Create a color picker with a label.

        Parameters
        ----------
        label : str
            Label text.
        name : str
            Form field name.
        value : str
            Initial color (#rrggbb).
        **attrs : Additional attributes.

        Returns
        -------
        Div containing label and color input.
        """
        from .html import Div, Label
        field_id = "miki-color-" + name

        return Div(
            Label(label, for_=field_id, class_="miki-colorpicker-label"),
            Input(
                type="color",
                name=name,
                value=value,
                id=field_id,
                class_="miki-colorpicker-input",
            ),
            class_="miki-colorpicker",
        )


class Textarea(Component):
    """A styled ``<textarea>`` element.

    Parameters
    ----------
    *children : Content (usually empty)
    resize : str
        "both" (default), "vertical", "horizontal", or "none".
    auto_expand : bool
        Auto-expand height based on content.
    rows : int
        Number of rows (default: 4).
    **attrs : Additional HTML attributes.
    """

    tag = "textarea"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        resize = attrs.pop("resize", "both")
        auto_expand = attrs.pop("auto_expand", False)

        attrs.setdefault("class", "miki-textarea")
        attrs.setdefault("rows", 4)

        resize_classes = {
            "both": "miki-textarea-resize-both",
            "vertical": "miki-textarea-resize-y",
            "horizontal": "miki-textarea-resize-x",
            "none": "miki-textarea-resize-none",
        }
        attrs["class_"] = f"{attrs.get('class_', '')} {resize_classes.get(resize, '')}".strip()

        if auto_expand:
            attrs["x_bind:style.height"] = "'auto'; this.scrollHeight + 'px'"

        super().__init__(*children, **attrs)


class Checkbox(Input):
    """A styled checkbox input with label.

    Parameters
    ----------
    *children : Label text
    name : str
        Form field name.
    value : str
        Checkbox value.
    checked : bool
        Initial checked state.
    **attrs : Additional HTML attributes.
    """

    tag = "input"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "checkbox")
        attrs.setdefault("class", "miki-checkbox-input")

        label = children[0] if children else ""
        super().__init__(label, **attrs)

    @classmethod
    def toggle(cls, *children: Any, **attrs: Any) -> Any:
        """Create a toggle switch (styled checkbox).

        Returns a container with toggle switch styling.
        """
        from .html import Label, Span
        name = attrs.pop("name", "toggle")
        checked = attrs.pop("checked", False)

        input_el = cls(
            type="checkbox",
            name=name,
            checked=checked,
            class_="miki-toggle-input",
        )
        label = Label(
            Span(class_="miki-toggle-track"),
            Span(class_="miki-toggle-thumb"),
            class_="miki-toggle-label",
        )
        return Div(input_el, label, class_="miki-toggle-wrapper")


class Radio(Input):
    """A styled radio button input.

    Parameters
    ----------
    *children : Label text
    name : str
        Form field group name.
    value : str
        Radio button value.
    checked : bool
        Initial checked state.
    **attrs : Additional HTML attributes.
    """

    tag = "input"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "radio")
        attrs.setdefault("class", "miki-radio-input")

        label = children[0] if children else ""
        super().__init__(label, **attrs)

    @classmethod
    def group(
        cls,
        name: str,
        options: list[tuple[str, str]],
        value: str | None = None,
        **attrs: Any,
    ) -> Any:
        """Create a group of radio buttons.

        Parameters
        ----------
        name : str
            Shared name for the radio group.
        options : list of (value, label) tuples.
        value : str | None
            Pre-selected value.
        **attrs : Additional attributes.

        Returns a container with all radio buttons and labels.
        """
        from .html import Div, Label
        radios = []
        for val, label in options:
            checked = attrs.pop("checked", value == val)
            radios.append(
                Label(
                    cls(type="radio", name=name, value=val, checked=checked),
                    str(label),
                    class_="miki-radio-group-item",
                )
            )
        return Div(*radios, class_="miki-radio-group")


class Slider(Input):
    """A styled range slider input.

    Parameters
    ----------
    *children : Label text (optional)
    min : int
        Minimum value (default: 0).
    max : int
        Maximum value (default: 100).
    value : int | float
        Initial value.
    step : int | float
        Step increment (default: 1).
    **attrs : Additional HTML attributes.
    """

    tag = "input"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "range")
        attrs.setdefault("class", "miki-slider")

        label = children[0] if children else ""
        super().__init__(label, **attrs)

    @classmethod
    def named(
        cls,
        label: str,
        name: str,
        value: int = 50,
        min: int = 0,
        max: int = 100,
        **attrs: Any,
    ) -> Any:
        """Create a slider with a label.

        Parameters
        ----------
        label : str
            Label text.
        name : str
            Form field name.
        value, min, max : int
            Slider configuration.
        **attrs : Additional attributes.

        Returns a container with label and slider.
        """
        from .html import Label, Span, Div

        display_value = Span(str(value), class_="miki-slider-value")

        return Div(
            Label(
                label,
                for_=name,
                class_="miki-slider-label",
            ),
            cls(
                type="range",
                name=name,
                value=value,
                min=min,
                max=max,
                class_="miki-slider-input",
            ),
            display_value,
            class_="miki-slider-wrapper",
        )


class Switch(Input):
    """A modern switch/checkbox toggle.

    Looks like iOS/macOS style switch control.
    """

    tag = "input"

    def __init__(self, *children: Any, **attrs: Any) -> None:
        attrs.setdefault("type", "checkbox")
        attrs.setdefault("class", "miki-switch-input")

        super().__init__(*children, **attrs)

    @classmethod
    def toggle(
        cls,
        name: str,
        label: str = "",
        checked: bool = False,
        **attrs: Any,
    ) -> Any:
        """Create a modern toggle switch.

        Parameters
        ----------
        name : str
            Form field name.
        label : str
            Optional label text.
        checked : bool
            Initial checked state.

        Returns a container with switch and optional label.
        """
        from .html import Label, Span, Div

        input_el = cls(type="checkbox", name=name, checked=checked, class_="miki-switch")

        if label:
            return Label(
                input_el,
                Span(class_="miki-switch-track"),
                Span(class_="miki-switch-thumb"),
                Span(label, class_="miki-switch-label-text"),
                class_="miki-switch-wrapper",
            )

        return Label(input_el, Span(class_="miki-switch-track"), Span(class_="miki-switch-thumb"), class_="miki-switch-wrapper")


class Select(Component):
    """A styled select dropdown.

    Parameters
    ----------
    *options : Option instances or (value, label) tuples.
    name : str
        Form field name.
    searchable : bool
        Allow text search (requires Alpine.js).
    multiple : bool
        Allow multiple selection.
    **attrs : Additional HTML attributes.
    """

    tag = "select"

    def __init__(self, *options: Any, **attrs: Any) -> None:
        name = attrs.pop("name", "")
        searchable = attrs.pop("searchable", False)
        multiple = attrs.pop("multiple", False)

        attrs.setdefault("class", "miki-select")
        attrs.setdefault("name", name)

        if searchable:
            attrs["x_data"] = "{search:''}"
            attrs["x_on:input"] = "updateOptions($el)"

        super().__init__(*options, **attrs)


class Option(Component):
    """An option element for select dropdowns."""

    tag = "option"

    def __init__(self, *children: Any, value: str = "", selected: bool = False, **attrs: Any) -> None:
        if value:
            attrs["value"] = value
        if selected:
            attrs["selected"] = True
        super().__init__(*children, **attrs)


class Upload(Component):
    """A file upload input with preview.

    Parameters
    ----------
    name : str
        Form field name.
    accept : str
        File types to accept (e.g., "image/*" or ".pdf,.doc").
    multiple : bool
        Allow multiple files.
    label : str
        Button label.
    **attrs : Additional HTML attributes.
    """

    tag = "div"

    def __init__(
        self,
        name: str = "file",
        accept: str = "*",
        multiple: bool = False,
        label: str = "Upload",
        **attrs: Any,
    ) -> None:
        from .html import Input as HTMLInput

        attrs.setdefault("class", "miki-upload")

        input_id = f"miki-upload-{name}"

        elements = [
            HTMLInput(
                type="file",
                name=name,
                id=input_id,
                accept=accept,
                multiple=multiple,
                class_="miki-upload-input",
                **{"x_on:change": "handleFileUpload($event)"},
            ),
        ]

        super().__init__(*elements, **attrs)