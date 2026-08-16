"""Step 5: Plugins

Demonstrates the plugin system: a custom theme plugin, a component plugin,
and an analytics plugin that hooks into rendering.
"""
from mikiui import MikiApp, Div, H1, P, Plugin, ThemePlugin
from mikiui.components import Component

app = MikiApp(title="Step 5: Plugins")


# --- Theme Plugin ---

class OceanTheme(ThemePlugin):
    """A simple color-theme plugin."""

    name = "ocean"

    def theme(self):
        from mikiui import Theme

        return Theme(
            name="ocean",
            source="plugin",
            css_path="/_miki/runtime/themes/ocean.css",
            extra_classes=["data-theme-ocean"],
            variables={
                "--miki-primary": "#0ea5e9",
                "--miki-bg": "#f0f9ff",
                "--miki-text": "#0c4a6e",
            },
        )


# --- Component Plugin ---

class StarRating(Component):
    """A simple star rating component."""

    tag = "span"

    def __init__(self, value, max_value=5, **attrs):
        filled = "★" * int(value)
        empty = "☆" * (int(max_value) - int(value))
        super().__init__(filled + empty, **attrs)


class ComponentsPlugin(Plugin):
    name = "components"

    def components(self):
        return {"StarRating": StarRating}


# --- Analytics Plugin ---

class AnalyticsPlugin(Plugin):
    """Injects a tracking snippet on every page."""

    name = "analytics"

    def on_render(self, tree):
        tree.append(
            Div("<!-- Analytics: page view tracked -->", class_="sr-only")
        )
        return tree


# Register plugins
app.use(OceanTheme())
app.use(ComponentsPlugin())
app.use(AnalyticsPlugin())
app.set_theme("ocean")


# --- Routes using registered components ---

@app.route("/")
def home():
    return Div(
        H1("Plugin Demo"),
        P("This page uses the Ocean theme and registered components."),
        StarRating(4, max_value=5, class_="text-2xl"),
        class_="max-w-2xl mx-auto p-8",
    )


@app.route("/about")
def about():
    return Div(
        H1("About"),
        P("Built with MikiUI plugins."),
        class_="max-w-2xl mx-auto p-8",
    )


if __name__ == "__main__":
    app.run()
