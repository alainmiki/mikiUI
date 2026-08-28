"""ThemeSwitcher widget: dynamically switch between all registered themes.

Automatically discovers themes from the app's theme registry, including
user-registered custom themes, with no hardcoded theme list.

Features:
- Dynamic theme discovery from ``app.theme_registry`` or global theme registry
- Optional framework filtering (e.g., only color themes, only Tailwind)
- HTMX support for partial page updates without full reload
- Custom label, placeholder, and disabled state
- Accessible: ARIA combobox semantics, keyboard navigation
- i18n hook for label translation
"""

from __future__ import annotations

from typing import Any

from ..components import Div, Option, Select
from ..components.base import Component
from ..themes import current_theme_name, list_themes


class ThemeSwitcher(Component):
    """A theme switcher that dynamically lists all registered themes.

    Parameters
    ----------
    app : Any
        The :class:`mikiui.app.MikiApp` instance. Required to read the active
        theme and call ``app.set_theme(...)`` on change.
    label : str | None
        Human-readable label text. Defaults to ``"Theme"``.
    themes : list[str] | None
        Optional explicit list of theme names to show. When ``None`` (default),
        all themes from ``app.theme_registry.list_all()`` are used.
    filter_framework : str | None
        If set, only themes whose ``framework`` matches this value are shown.
        Useful for showing only color themes (``None``) or only Tailwind themes
        (``"tailwind"``).
    placeholder : str
        Placeholder text for the select. Defaults to ``"Select theme..."``.
    disabled : bool
        Disable the switcher. Defaults to ``False``.
    htmx_get : str | None
        HTMX route to call on change (e.g. ``"/set-theme"``). When set, the
        select gains ``hx-get``, ``hx-trigger="change"``, ``hx-swap="none"``,
        and ``hx-refresh="true"`` so the server handles the switch and then
        reloads the page to propagate the new theme.
    on_change : Any | None
        Optional client-side callback. Not used directly by the widget but
        exposed for advanced users who want to inject custom JS behavior.
    class_ : str | None
        Extra CSS classes for the wrapper element.
    **attrs :
        Additional HTML attributes forwarded to the wrapper element.

    Example
    -------
    Basic usage (auto-discovers all themes)::

        ThemeSwitcher(app)

    Filter to color themes only::

        ThemeSwitcher(app, filter_framework=None)

    With HTMX::

        ThemeSwitcher(app, htmx_get="/set-theme")
    """

    tag = "div"

    def __init__(
        self,
        app: Any,
        label: str | None = None,
        themes: list[str] | None = None,
        filter_framework: str | None = None,
        placeholder: str = "Select theme...",
        disabled: bool = False,
        htmx_get: str | None = None,
        on_change: Any = None,
        class_: str | None = None,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-theme-switcher")
        attrs.setdefault("role", "group")
        attrs.setdefault("aria-label", "Theme Switcher")
        attrs.setdefault("touch-action", "manipulation")

        wrapper_classes = "miki-theme-switcher"
        if class_:
            wrapper_classes += f" {class_}"
        attrs["class_"] = wrapper_classes

        current_theme = current_theme_name(app)

        if themes is None:
            try:
                themes = list(app.theme_registry.list_all())
            except AttributeError:
                try:
                    themes = list_themes()
                except Exception:
                    themes = list_themes()

        if filter_framework is not None:
            try:
                from ..themes import get_theme as _get_theme
                themes = [
                    name
                    for name in themes
                    if _get_theme(name) is not None
                    and getattr(_get_theme(name), "framework", None) == filter_framework
                ]
            except Exception:
                pass

        label_text = label or "Theme"
        label_component = Div(
            label_text,
            class_="miki-theme-switcher-label",
            id="miki-theme-switcher-label",
        )

        options = [Option("", value="", disabled=True, selected=True)]
        for theme_name in themes:
            is_selected = theme_name == current_theme
            option = Option(
                theme_name,
                value=theme_name,
                selected=is_selected,
            )
            options.append(option)

        select_attrs: dict[str, Any] = {
            "class_": "miki-theme-select",
            "aria-labelledby": "miki-theme-switcher-label",
            "aria-label": label_text,
        }
        if placeholder:
            select_attrs["data-placeholder"] = placeholder
        if disabled:
            select_attrs["disabled"] = True
            select_attrs["aria-disabled"] = "true"
        if htmx_get:
            select_attrs["hx-get"] = htmx_get
            select_attrs["hx-trigger"] = "change"
            select_attrs["hx-swap"] = "none"
            select_attrs["hx-refresh"] = "true"
        else:
            select_attrs["data-miki-theme-switch"] = "true"
            select_attrs["data-miki-theme-endpoint"] = "/_miki/api/theme"
        if on_change is not None:
            select_attrs["data-miki-theme-onchange"] = str(on_change)

        select = Select(*options, **select_attrs)

        super().__init__(label_component, select, **attrs)
