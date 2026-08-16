"""08_plugins.py — Plugin ecosystem showcase.

Demonstrates ThemePlugin, ComponentPlugin, and WidgetPlugin with
custom Midnight theme, Alert component, and WeatherWidget.

Run with: mikiui dev --app mikiui.examples.08_plugins:app
"""

from __future__ import annotations

from mikiui import Div, H1, H2, H3, MikiApp, P, register_theme
from mikiui.app.plugins import ComponentPlugin, Plugin, ThemePlugin, WidgetPlugin
from mikiui.components import Button, Navbar
from mikiui.themes import Theme
from mikiui.widgets import Card
from mikiui.widgets.layout_widgets import Footer


class HelloPlugin(Plugin):
    """A simple plugin that adds a greeting helper."""

    name = "hello"
    depends_on: list[str] = []

    def register(self, app: MikiApp) -> None:
        app._hello_count = 0

        def hello_world() -> str:
            app._hello_count += 1
            return f"Hello #{app._hello_count} from the plugin system."

        app.hello_world = hello_world


class MidnightThemePlugin(ThemePlugin):
    """Registers a custom 'midnight' theme with deep blue tones."""

    name = "midnight-theme"

    def theme(self) -> Theme:
        return Theme(
            name="midnight",
            source="plugin",
            framework="css",
            variables={
                "--miki-bg": "#0f172a",
                "--miki-fg": "#e2e8f0",
                "--miki-accent": "#38bdf8",
                "--miki-card": "#1e293b",
                "--miki-border": "#334155",
            },
            extra_classes=["miki-theme-midnight"],
        )


class AlertComponentPlugin(ComponentPlugin):
    """Adds a custom Alert component for notices."""

    name = "alert-component"

    def components(self) -> dict[str, type]:
        from mikiui.components import Div as _Div

        class Alert(_Div):
            tag = "div"

            def __init__(self, message: str, level: str = "info", **attrs: object) -> None:
                colors = {
                    "info": "blue",
                    "success": "emerald",
                    "warning": "amber",
                    "error": "red",
                }
                color = colors.get(level, "slate")
                attrs.setdefault("class_", f"alert alert-{level} bg-{color}-50 border border-{color}-200 text-{color}-800 p-4 rounded-lg")
                attrs.setdefault("role", "alert")
                super().__init__(message, **attrs)

        return {"Alert": Alert}


class WeatherWidgetPlugin(WidgetPlugin):
    """Adds a simple WeatherWidget that shows mock forecast data."""

    name = "weather-widget"

    def widgets(self) -> dict[str, type]:
        from mikiui.components import Div as _Div
        from mikiui.components.html import Img as _Img

        class WeatherWidget(_Div):
            tag = "div"

            def __init__(self, city: str = "Lisbon", **attrs: object) -> None:
                attrs.setdefault("class_", "weather-widget bg-white p-5 rounded-xl shadow-sm border border-slate-100")
                forecast = [
                    ("Mon", "24°C", "Sunny", "https://openweathermap.org/img/wn/01d@2x.png"),
                    ("Tue", "22°C", "Cloudy", "https://openweathermap.org/img/wn/03d@2x.png"),
                    ("Wed", "19°C", "Rain", "https://openweathermap.org/img/wn/10d@2x.png"),
                    ("Thu", "21°C", "Partly Cloudy", "https://openweathermap.org/img/wn/02d@2x.png"),
                    ("Fri", "25°C", "Sunny", "https://openweathermap.org/img/wn/01d@2x.png"),
                ]
                days = []
                for day, temp, desc, icon in forecast:
                    days.append(
                        Div(
                            _Img(src=icon, alt=desc, class_="w-10 h-10 mx-auto"),
                            P(day, class_="text-xs font-medium text-slate-500 mt-2"),
                            P(temp, class_="text-sm font-bold text-slate-800"),
                            P(desc, class_="text-[10px] text-slate-400"),
                            class_="flex flex-col items-center",
                        )
                    )
                super().__init__(
                    Div(
                        H3(f"Weather in {city}", class_="text-lg font-bold text-slate-800 mb-1"),
                        P("Next 5 days forecast", class_="text-xs text-slate-500 mb-4"),
                        Div(*days, class_="flex justify-between"),
                    ),
                    **attrs,
                )

        return {"WeatherWidget": WeatherWidget}


app = MikiApp(title="Plugin Ecosystem", lang="en")
app.use(HelloPlugin())
app.use(MidnightThemePlugin())
app.use(AlertComponentPlugin())
app.use(WeatherWidgetPlugin())


@app.route("/")
def home() -> Div:
    return Div(
        Navbar(brand="Plugin Ecosystem", links=[("Home", "/"), ("Plugins", "/plugins"), ("Docs", "/docs")], dark=True),
        Div(
            Div(
                H1("Plugin Ecosystem", class_="text-4xl font-extrabold text-slate-900 mb-2"),
                P("Extend MikiUI with themes, components, and widgets.", class_="text-lg text-slate-600 mb-8"),
                Card(
                    P("Plugin greeting:", class_="text-sm text-slate-500"),
                    P(app.hello_world(), class_="text-xl font-semibold text-indigo-600"),
                    class_="max-w-xl p-6 mb-8",
                ),
                class_="max-w-6xl mx-auto",
            ),
            Div(
                H2("Built-in Plugins", class_="text-2xl font-bold text-slate-800 mb-6"),
                Div(
                    Card(H3("ThemePlugin", class_="font-semibold mb-2"), P("Registers new color palettes, CSS variables, and font stacks without touching core code."), class_="p-6"),
                    Card(H3("ComponentPlugin", class_="font-semibold mb-2"), P("Injects reusable component classes (Alert, Toast, Tag) into the component registry."), class_="p-6"),
                    Card(H3("WidgetPlugin", class_="font-semibold mb-2"), P("Adds high-level widgets like WeatherWidget, StockTicker, or a custom Calendar view."), class_="p-6"),
                    class_="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12",
                ),
                class_="max-w-6xl mx-auto",
            ),
            Div(
                H2("Custom Plugins in Action", class_="text-2xl font-bold text-slate-800 mb-6"),
                Div(
                    Div(
                        H3("Midnight Theme", class_="font-semibold mb-3"),
                        P("The MidnightThemePlugin registers a dark palette with deep blues and sky accents.", class_="text-slate-600 mb-4"),
                        Div(
                            Button("Activate Midnight", variant="primary", hx_post="/api/plugins/theme/midnight", hx_target="#theme-status", hx_swap="innerHTML"),
                            Div(id="theme-status", class_="mt-3"),
                            class_="max-w-xs",
                        ),
                        class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100 mb-6",
                    ),
                    Div(
                        H3("Alert Component", class_="font-semibold mb-3"),
                        P("The AlertComponentPlugin injects an Alert component with info, success, warning, and error levels.", class_="text-slate-600 mb-4"),
                        Div(
                            Button("Trigger Info", variant="secondary", class_="mr-2"),
                            Button("Trigger Success", variant="primary", class_="mr-2"),
                            Button("Trigger Error", variant="secondary", class_="text-red-700"),
                            class_="flex flex-wrap gap-2",
                        ),
                        class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100 mb-6",
                    ),
                    Div(
                        H3("WeatherWidget", class_="font-semibold mb-3"),
                        P("The WeatherWidgetPlugin provides a forecast widget powered by mock data.", class_="text-slate-600 mb-4"),
                        Div(
                            Card(WeatherWidgetPlugin().widgets()["WeatherWidget"]("Porto"), class_="max-w-sm"),
                            class_="mt-4",
                        ),
                        class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100",
                    ),
                    class_="max-w-4xl space-y-6",
                ),
                class_="max-w-6xl mx-auto mb-12",
            ),
            Div(
                H2("Dependency Graph", class_="text-2xl font-bold text-slate-800 mb-4"),
                P("Plugins declare dependencies. MikiUI validates the order before registration.", class_="text-slate-600 mb-4"),
                Div(
                    P("HelloPlugin → (none)", class_="text-sm text-slate-600"),
                    P("MidnightThemePlugin → (none)", class_="text-sm text-slate-600"),
                    P("AlertComponentPlugin → (none)", class_="text-sm text-slate-600"),
                    P("WeatherWidgetPlugin → (none)", class_="text-sm text-slate-600"),
                    class_="bg-white p-6 rounded-xl shadow-sm border border-slate-100 font-mono text-sm space-y-1",
                ),
                class_="max-w-6xl mx-auto mb-12",
            ),
            class_="space-y-6",
        ),
        Footer(
            copyright="© 2026 MikiUI Plugin Ecosystem",
        ),
        class_="min-h-screen bg-slate-50",
    )


@app.route("/api/plugins/theme/midnight", methods=["POST"])
async def activate_midnight(ctx) -> Div:
    app.set_theme("midnight")
    return Div(P("Midnight theme activated.", class_="text-emerald-600 font-semibold"))


@app.route("/plugins")
def plugins_page() -> Div:
    return Div(
        Navbar(brand="Plugin Ecosystem", links=[("Home", "/")]),
        Div(
            H1("Available Plugins", class_="text-3xl font-bold text-slate-900 mb-6"),
            Div(
                Card(H3("hello", class_="font-semibold"), P("Greeting helper. No dependencies."), class_="p-6"),
                Card(H3("midnight-theme", class_="font-semibold"), P("Dark theme plugin. No dependencies."), class_="p-6"),
                Card(H3("alert-component", class_="font-semibold"), P("Alert component. No dependencies."), class_="p-6"),
                Card(H3("weather-widget", class_="font-semibold"), P("Weather forecast widget. No dependencies."), class_="p-6"),
                class_="grid grid-cols-1 md:grid-cols-2 gap-6",
            ),
            class_="max-w-4xl mx-auto py-12",
        ),
    )


if __name__ == "__main__":
    app.run()
