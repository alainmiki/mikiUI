# MikiUI Plugin System

Plugins extend MikiUI apps with custom themes, components, widgets, and render-time transformations. Register plugins via `app.use(plugin)`.

## Base Plugin

The `Plugin` base class provides three hooks:

```python
from mikiui.app import Plugin

class MyPlugin(Plugin):
    name = "my-plugin"

    def register(self, app):
        """Called once when app.use(plugin) is invoked."""
        pass

    def on_render(self, tree):
        """Modify the component tree before it is rendered to HTML."""
        return tree

    def on_request(self, request):
        """Called for every incoming request (e.g. analytics, auth, metrics)."""
        # Modify request state, add headers, etc.
        return request

app.use(MyPlugin())
```

**Parameters:**

| Hook | Description |
|------|-------------|
| `register(app)` | Initialize plugin with the app. Access `app.state` for shared data. |
| `on_render(tree)` | Transform the component tree. Return a modified list of nodes. |
| `on_request(request)` | Middleware-style hook for requests. Modify request headers or app state. |

---

## Theme Plugins

### Color Theme Plugin

Register a color theme that sets CSS variables:

```python
from mikiui.app import Plugin, Theme, ThemePlugin

class CorporateTheme(ThemePlugin):
    """Theme plugin that provides a custom color scheme."""

    def theme(self):
        return Theme(
            name="corporate",
            source="plugin",
            css_path="/_miki/runtime/corporate.css",  # Path relative to runtime
            extra_classes=["data-theme-corporate"],    # Body classes
            variables={
                "--miki-primary": "#0066cc",
                "--miki-bg": "#ffffff",
            },
        )

class MyPlugin(Plugin):
    def register(self, app):
        corporate = CorporateTheme()
        app.register_theme(corporate.theme())
        app.set_theme("corporate")
```

### Framework Theme Plugin (Tailwind/Bootstrap)

Provide a framework-based theme:

```python
from mikiui.app import Plugin, Theme

class TailwindPlugin(Plugin):
    """Plugin that provides Tailwind CSS with DaisyUI."""

    def register(self, app):
        theme = Theme(
            name="tailwind-da",
            framework="tailwind",
            cdn_url="https://unpkg.com/tailwindcss@3/dist/tailwind.min.css",
            css_path="/_miki/runtime/themes/light.css",  # Color theme
            extra_classes=["data-theme=mikiui-light"],
            tailwind_config={
                "daisyui": {
                    "themes": ["mikiui-light", "mikiui-dark"],
                }
            },
        )
        app.register_theme(theme)

app.use(TailwindPlugin())
app.set_theme("tailwind-da")
```

### Plugin-Supplied Theme (Simple Pattern)

The `ThemePlugin` base class simplifies theme registration:

```python
from mikiui.app import ThemePlugin, Theme

class MyThemePlugin(ThemePlugin):
    """Simplest theme plugin pattern."""

    def theme(self):
        return Theme(
            name="dark-theme",
            source="plugin",
            framework="tailwind",  # or "bootstrap", None
            cdn_url="https://cdn.example.com/tailwind.css",
            css_path="/_miki/runtime/themes/dark.css",
            variables={"--miki-primary": "#8b5cf6"},
        )

# The plugin auto-registers when used
app.use(MyThemePlugin())
```

---

## Component Plugins

Register custom component classes for use in your app:

```python
from mikiui.app import ComponentPlugin
from mikiui.components.base import Component

class Rating(Component):
    """A star rating component."""

    tag = "span"

    def __init__(self, value, max_value=5, **attrs):
        stars = "★" * int(value) + "☆" * (int(max_value) - int(value))
        super().__init__(stars, **attrs)

class MyComponents(ComponentPlugin):
    def components(self):
        return {"Rating": Rating}

app.use(MyComponents())

# Now you can use Rating as a regular component
@app.route("/")
def home():
    return Rating(4, max_value=5, class_="text-2xl")
```

**Accessing registered components:**

```python
# After app.use(MyComponents())
ratings = app._component_registry["Rating"]
```

---

## Widget Plugins

Register composite widgets built from components:

```python
from mikiui.app import WidgetPlugin
from mikiui.components import Div, Button, Input

class SearchWidget:
    """A composite search widget with input and suggestions."""

    def __init__(self, placeholder="Search...", suggestions=None):
        self.placeholder = placeholder
        self.suggestions = suggestions or []

    def render(self):
        from mikiui import List, ListItem
        return Div(
            Input(type="text", placeholder=self.placeholder),
            List([ListItem(s) for s in self.suggestions]) if self.suggestions else "",
            class_="search-widget",
        )

class MyWidgets(WidgetPlugin):
    def widgets(self):
        return {"Search": SearchWidget}

app.use(MyWidgets())
```

**Accessing registered widgets:**

```python
widgets = app._widget_registry["Search"]
search = widgets.Search(placeholder="Enter name...", suggestions=["Alice", "Bob"])
```

---

## Render-Time Transformations

Modify the component tree or request processing:

```python
from mikiui.app import Plugin
from mikiui.components import Div, Span

class AnalyticsPlugin(Plugin):
    """Inject analytics and modify HTML output."""

    def on_render(self, tree):
        """Add a tracking pixel or modify elements."""
        from mikiui import P
        tree.append(P("<!-- Analytics tracking -->", class_="sr-only"))
        return tree

    def on_request(self, request):
        """Add request metadata to app state."""
        request.state.analytics_id = self._generate_id()
        return request

    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())[:8]

app.use(AnalyticsPlugin())
```

---

## Accessing Plugin Data

Plugins can store data on the app:

```python
from mikiui.app import Plugin

class ConfigMap(Plugin):
    name = "config"

    def register(self, app):
        self.config = {
            "api_endpoint": "https://api.example.com",
            "feature_flags": {"new_ui": True},
        }
        app.state.config = self.config
        app.state.feature_flags = self.config["feature_flags"]

app.use(ConfigMap())

# Access anywhere
@app.post("/action")
def handle_action(ctx):
    api = ctx.app.state.config["api_endpoint"]
    if ctx.app.state.feature_flags.get("new_ui"):
        # ...
```

---

## Multiple Plugins

Use multiple plugins in any order:

```python
from mikiui import MikiApp, Theme, ThemePlugin

app = MikiApp(title="Multi-Plugin App")

# Each plugin can add its own functionality
app.use(AnalyticsPlugin())
app.use(ThemePlugin())  # Custom theme
app.use(MyComponentPlugin())
app.use(MyWidgetPlugin())

# Plugins are applied in order on_render
for plugin in app.plugins:
    tree = plugin.on_render(tree)
```

---

## Plugin Template

Start a new plugin with this template:

```python
from mikiui.app import Plugin, Theme, ThemePlugin

class MyFeaturePlugin(Plugin):
    """Brief description of what this plugin does."""

    name = "my-feature"

    def register(self, app):
        """Initialize everything needed for this plugin."""
        # Register themes, components, widgets
        # Modify app state
        # Set up routes if needed
        pass

    def on_render(self, tree):
        """Transform the component tree before rendering."""
        # Add elements, modify existing ones
        # Return the modified tree
        return tree

    def on_request(self, request):
        """Process each request."""
        # Add authentication, logging, etc.
        return request

# Usage
app = MikiApp()
app.use(MyFeaturePlugin())
```

---

## Security Notes

- **Isolation**: Plugins run in the same process as the application. Only install trusted plugins.
- **Performance**: `on_render` and `on_request` hooks are called for every request. Keep them fast.
- **Async I/O**: Use `await` in `on_request` for database/network operations.
- **State sharing**: Use `app.state` to share data between plugins and handlers.

---

## Distribution

Publish a plugin package:

**pyproject.toml:**
```toml
[project]
name = "mikiui-theme-dark-mod"
version = "1.0.0"
dependencies = ["mikiui"]

[project.entry-points."mikiui.plugins"]
dark_mod = "mikiui_theme_dark_mod.plugin:DarkModPlugin"
```

**Installation:**
```bash
pip install mikiui-theme-dark-mod
```

**Usage:**
```python
from mikiui import MikiApp
from mikiui_theme_dark_mod import DarkModPlugin  # Registered via entry-point

app = MikiApp()
app.use(DarkModPlugin())
```