# Plugins

Plugins extend MikiUI apps with custom themes, components, widgets, backend routes, middleware, and render-time transformations.

## Architecture

MikiUI plugins are Python classes registered via `app.use(plugin)`:

```python
from mikiui.app.plugins import Plugin

class MyPlugin(Plugin):
    def register(self, app):
        # Initialize plugin
        pass

    def on_request(self, request):
        # Called on every request
        pass

    def on_render(self, tree):
        # Transform component tree before rendering
        return tree

app.use(MyPlugin())
```

## Plugin Types

- **ThemePlugin** — adds custom themes
- **ComponentPlugin** — registers custom components
- **WidgetPlugin** — registers custom widgets
- **BackendPlugin** — adds FastAPI routes and middleware

## Creating a Plugin

```python
from mikiui.app.plugins import Plugin, ComponentPlugin
from mikiui import Button

class HelloPlugin(ComponentPlugin):
    def register(self, app):
        # Register a custom component
        app.register_component("hello-button", HelloButton)
```

## Dependency Ordering

Plugins can declare `depends_on` to control registration order:

```python
class AnalyticsPlugin(Plugin):
    depends_on = ["auth"]  # auth plugin must be registered first
```

Missing dependencies raise `RuntimeError` at registration time.

## Distribution

Plugins can be distributed as Python packages and discovered via entry points:

```toml
# pyproject.toml
[project.entry-points."mikiui.plugins"]
my-plugin = "my_plugin:MyPlugin"
```

## Security

MikiUI validates every plugin before loading:

1. **Manifest identity** — plugin name matches its manifest
2. **Capability check** — declared capabilities are not globally blocked
3. **AST vetting** — source code is scanned for dangerous patterns
4. **Import scanning** — only allow-listed modules may be imported

### Plugin Configuration

```python
from mikiui.app import PluginSecurityConfig

config = PluginSecurityConfig(
    allow_untrusted=False,
    vet_ast=True,
    blocked_capabilities=["filesystem:write"],
)
app.set_plugin_security_config(config)
```

## Marketplace

Install plugins from a directory or PyPI-like index:

```python
from mikiui.app import DirectoryIndexSource, PluginMarketplace

source = DirectoryIndexSource("mikiui_plugins")
market = PluginMarketplace(source)
plugin = market.install("chart-widget", app)
```

## See Also

- [Security Guide](../guide/security.md#plugin-security) — plugin security model
- [API Reference](../guide/api-reference.md) — plugin API
- [Contributing](../guide/contributing.md) — publishing plugins
