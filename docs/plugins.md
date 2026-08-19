# Plugin Development Guide

Plugins extend MikiUI apps with custom themes, components, widgets,
backend routes, middleware, and render-time transformations. This guide covers
the plugin architecture, creation workflow, distribution, and security.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Creating a Plugin](#creating-a-plugin)
- [Plugin Types](#plugin-types)
- [Plugin Hooks Reference](#plugin-hooks-reference)
- [Distribution and Discovery](#distribution-and-discovery)
- [Security Considerations](#security-considerations)

---

## Architecture Overview

MikiUI plugins are Python classes registered via `app.use(plugin)`. They run
in-process and participate in the full app lifecycle:

```
Plugin Registration
  └─ app.use(plugin)
       └─ plugin.configure(config)        # optional config
       └─ plugin.register(app)            # initialize

Per-Request Lifecycle
  └─ plugin.on_request(request)           # every incoming request
  └─ route handler executes
  └─ plugin.on_render(tree)               # transform output
  └─ HTTP response sent

Shutdown
  └─ plugin.on_shutdown()                 # cleanup
```

### Dependency Ordering

Plugins can declare `depends_on` to control registration order:

```python
class AnalyticsPlugin(Plugin):
    depends_on = ["auth"]   # auth plugin must be registered first
```

Missing dependencies raise `RuntimeError` at registration time.

### Plugin Registry

MikiUI maintains three registries accessible from `app`:

| Registry | Access | Purpose |
|----------|--------|---------|
| `app.plugins` | `list[Plugin]` | All registered plugins |
| `app.registry` | `WidgetRegistry` | Components and widgets |
| `app.theme_registry` | `ThemeRegistry` | Available themes |

---

## Creating a Plugin

### Step 1: Subclass `Plugin`

```python
from mikiui import Plugin

class MyPlugin(Plugin):
    name = "my-plugin"

    def register(self, app):
        print(f"{self.name} registered")
```

### Step 2: Register with the App

```python
from mikiui import MikiApp

app = MikiApp()
app.use(MyPlugin())
```

### Step 3: Add Functionality

Override hooks to add behavior:

```python
class AnalyticsPlugin(Plugin):
    name = "analytics"

    def on_request(self, request):
        request.state.request_id = generate_id()
        return request

    def on_render(self, tree):
        tree.append(P("<!-- Analytics -->", class_="sr-only"))
        return tree

    def on_error(self, error, request):
        log_error(error, request.state.request_id)
```

---

## Plugin Types

### Theme Plugins

Register a custom color theme:

```python
from mikiui import ThemePlugin, Theme

class DarkMod(ThemePlugin):
    name = "dark-mod"

    def theme(self) -> Theme:
        return Theme(
            name="dark-mod",
            source="plugin",
            css_path="/_miki/runtime/dark-mod.css",
            extra_classes=["data-theme-dark-mod"],
            variables={
                "--miki-primary": "#8b5cf6",
                "--miki-bg": "#0f172a",
                "--miki-text": "#f8fafc",
            },
        )

app.use(DarkMod())
app.set_theme("dark-mod")
```

### Component Plugins

Register reusable components:

```python
from mikiui import ComponentPlugin
from mikiui.components import Component, Span

class StarRating(Component):
    tag = "span"

    def __init__(self, value, max_value=5, **attrs):
        stars = "★" * int(value) + "☆" * (int(max_value) - int(value))
        super().__init__(stars, **attrs)

class MyComponents(ComponentPlugin):
    name = "my-components"

    def components(self) -> dict[str, type]:
        return {"StarRating": StarRating}

app.use(MyComponents())
```

### Widget Plugins

Register composite widgets:

```python
from mikiui import WidgetPlugin
from mikiui.components import Div, Input

class SearchWidget:
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
    name = "my-widgets"

    def widgets(self) -> dict[str, type]:
        return {"Search": SearchWidget}

app.use(MyWidgets())
```

### Backend Plugins

Add FastAPI routes and middleware:

```python
from mikiui import Plugin
from fastapi import APIRouter

class ApiPlugin(Plugin):
    name = "api"

    def register(self, app):
        self.router = APIRouter()

        @self.router.get("/api/health")
        async def health():
            return {"status": "ok"}

    def backend_routes(self) -> list[dict]:
        return [
            {
                "path": "/api/health",
                "methods": ["GET"],
                "endpoint": self.router.routes[0].endpoint,
                "include_in_schema": True,
                "name": "health",
                "tags": ["health"],
            }
        ]

    def middleware_classes(self) -> list[type]:
        return [CustomMiddleware]
```

### Notification Plugins

Handle global notifications and alerts:

```python
from mikiui import Plugin
from mikiui.widgets import NotificationPanel

class NotificationPlugin(Plugin):
    name = "notifications"

    def register(self, app):
        app.state.notifications = []

    def on_request(self, request):
        if "X-Notification" in request.headers:
            app.state.notifications.append(request.headers["X-Notification"])
        return request

    def on_render(self, tree):
        if app.state.notifications:
            tree.append(NotificationPanel(app.state.notifications))
            app.state.notifications.clear()
        return tree
```

---

## Plugin Hooks Reference

| Hook | When Called | Use Case |
|------|-------------|----------|
| `configure(config)` | Before `register`, if config passed to `app.use` | Set plugin options |
| `register(app)` | Once, when `app.use(plugin)` is called | Register themes, routes, state |
| `on_request(request)` | Every incoming request | Auth, logging, analytics |
| `on_route_add(path, methods, handler)` | When a route is registered | Route introspection, protection |
| `on_render(tree)` | After handler returns, before HTML | Wrap layouts, inject scripts |
| `on_error(error, request)` | When handler raises | Error logging, fallback UI |
| `on_shutdown()` | App shutdown | Cleanup, close connections |
| `assets()` | Build time | Return static asset paths |
| `backend_routes()` | Backend setup | Return FastAPI route defs |
| `middleware_classes()` | Backend setup | Return middleware classes |

---

## Plugin Manifest

Every plugin can ship a structured manifest that describes its identity,
capabilities, and compatibility.  MikiUI reads manifests at discovery time and
validates them before the plugin is loaded.

### Manifest sources (checked in order)

1. **Module-level dict** — ``PLUGIN_MANIFEST`` in the plugin module.
2. **`plugin.json` file** — next to the plugin module.
3. **Module attributes** — ``__name__``, ``__version__``, ``__doc__`` as fallback.

### Manifest schema

```python
from mikiui.app.plugin_security import PluginManifest

manifest = PluginManifest(
    name="my-plugin",             # unique identifier, must match plugin.name
    version="1.0.0",              # semver
    description="...",            # human-readable
    author="...",                 # maintainer
    license="MIT",                # SPDX identifier
    min_mikiui_version="0.1.0",   # minimum MikiUI version required
    dependencies=[],              # other plugin names this plugin requires
    capabilities=[],              # e.g. ["filesystem:read", "network:outbound"]
    homepage="...",               # optional URL
    repository="...",             # optional source URL
    source="builtin",             # "builtin" | "local" | "entry_point" | "marketplace"
    checksum="...",               # optional SHA-256 for integrity verification
)
```

### `plugin.json` example

```json
{
  "name": "chart-widget",
  "version": "2.1.0",
  "description": "Reactive chart widget",
  "author": "MikiUI Labs",
  "license": "MIT",
  "min_mikiui_version": "0.2.0",
  "dependencies": ["data-grid"],
  "capabilities": ["ui:render"],
  "source": "marketplace"
}
```

---

## Security & Sandboxing

MikiUI enforces a **security-first** plugin policy.  All plugins are validated
before registration, and the app can enforce a configurable allow/deny policy.

### Security policy

Configure the app's policy via ``PluginSecurityConfig``:

```python
from mikiui.app import MikiApp, PluginSecurityConfig

config = PluginSecurityConfig(
    allow_untrusted=False,       # only builtin/entry-point plugins allowed
    vet_ast=True,                # scan source for dangerous patterns
    blocked_capabilities=[],     # e.g. ["filesystem:write", "network:outbound"]
    allow_filesystem_write=False,
    allow_network=True,
    max_plugin_size_bytes=0,     # 0 = no limit
)

app = MikiApp(title="Secure App")
app.set_plugin_security_config(config)
```

### Auto-load

Discover and register all plugins (built-in + entry points + local dirs) in
dependency order:

```python
from mikiui.app.plugin_discovery import auto_load

app = MikiApp()
registered = auto_load(app, include_builtins=True, include_entry_points=True)
```

Plugins are registered in topological order based on ``depends_on`` so that
dependencies are satisfied before dependents.

### Import allowlist

The plugin validator scans all imports (including relative imports) against an
allowlist. Built-in modules like ``__future__``, ``os``, ``json``, etc. are
permitted by default. Plugins may also import ``mikiui`` and ``mikiui_app_plugins``.
Relative imports (e.g. ``from .session import X``) are resolved against the
plugin's full module path before validation.

### AST vetting

When ``vet_ast=True``, MikiUI parses plugin source code and blocks dangerous
patterns before the module is executed:

- ``subprocess.run``, ``subprocess.Popen``, ``subprocess.call``
- ``os.system``, ``os.popen``, ``os.spawn``, ``os.exec``
- ``shutil.rmtree``
- ``eval``, ``exec``, ``compile``, ``__import__``
- ``importlib.import_module``
- ``socket.socket``
- ``requests.post``, ``requests.get``
- ``aiohttp.ClientSession``

### Import allow-list

When ``allowed_imports`` is non-empty, only those top-level module names may be
imported.  When empty, the default safe list is used (stdlib + ``mikiui`` +
``mikiui_app_plugins`` + common web deps like ``fastapi``, ``starlette``,
``pydantic``).

Explicitly blocked imports always raise ``PluginSecurityViolation`` regardless
of the allow-list.

### Capability tokens

Plugins declare capabilities they require:

```python
class MyPlugin(Plugin):
    name = "my-plugin"
    capabilities = ["filesystem:read", "network:outbound"]
```

The app's ``blocked_capabilities`` list prevents any plugin from declaring
forbidden capabilities.

### Validation flow

1. **Discovery time** — ``discover_plugins()`` can reject plugins whose manifest
   or source violates policy.
2. **Registration time** — ``app.use()`` calls the validator before
   ``plugin.register(self)`` so even manually instantiated plugins are checked.

A plugin that fails validation raises ``PluginSecurityViolation`` and is **not
registered**.

---

## Marketplace

MikiUI includes a pluggable marketplace client for discovering, auditing, and
installing plugins from remote or local indexes.

### Quick start

```python
from mikiui.app import (
    MikiApp,
    PluginSecurityConfig,
    DirectoryIndexSource,
    PluginMarketplace,
)

config = PluginSecurityConfig(vet_ast=True, allow_untrusted=True)
source = DirectoryIndexSource("mikiui_plugins")
market = PluginMarketplace(source, security_config=config)

app = MikiApp(title="My App")
app.set_plugin_security_config(config)

# Search
results = market.search("chart")
for info in results:
    print(info.name, info.version, info.description)

# Install
plugin = market.install("chart-widget", app)
```

### Directory index

``DirectoryIndexSource`` scans a local directory of plugin packages.  Each
sub-directory should contain a ``plugin.json`` manifest and the plugin module.

```
mikiui_plugins/
  chart-widget/
    plugin.json
    chart_widget.py
  auth-plugin/
    plugin.json
    auth_plugin.py
```

### Remote index

``PyPIIndexSource`` wraps a PyPI-like JSON API for remote discovery:

```python
from mikiui.app import PyPIIndexSource

source = PyPIIndexSource("https://pypi.org/pypi")
market = PluginMarketplace(source)
```

### Custom backends

Implement ``MarketplaceSource`` to plug in any index backend:

```python
from mikiui.app.marketplace import MarketplaceSource, PluginInfo
from pathlib import Path

class MySource(MarketplaceSource):
    def search(self, query: str) -> list[PluginInfo]: ...
    def fetch(self, name: str, dest: Path) -> Path: ...
    def list_all(self) -> list[PluginInfo]: ...
```

### Security in the marketplace

Every plugin downloaded from a marketplace is validated through
``PluginValidator`` before it is loaded.  The app's security policy
(``allow_untrusted``, ``vet_ast``, ``blocked_capabilities``) applies.

```python
# Reject plugins that fail validation
try:
    plugin = market.install("unknown-plugin", app)
except PluginSecurityViolation as e:
    print(f"Plugin rejected: {e}")
```

### Bulk install

```python
installed = market.install_all(app)
print(f"Installed {len(installed)} plugins")
```

---

## Distribution and Discovery

### Package Structure

```
mikiui-theme-dark-mod/
  pyproject.toml
  mikiui_theme_dark_mod/
    __init__.py
    plugin.py
```

### pyproject.toml

```toml
[project]
name = "mikiui-theme-dark-mod"
version = "1.0.0"
description = "Dark mode theme for MikiUI"
dependencies = ["mikiui"]

[project.entry-points."mikiui.plugins"]
dark_mod = "mikiui_theme_dark_mod.plugin:DarkModPlugin"
```

### Installation

```bash
pip install mikiui-theme-dark-mod
```

### Auto-Discovery

When installed, the plugin is automatically available:

```python
from mikiui_theme_dark_mod import DarkModPlugin

app = MikiApp()
app.use(DarkModPlugin())
```

Or use the entry-point name if using a plugin loader:

```python
from mikiui import load_plugin

plugin = load_plugin("dark_mod")
app.use(plugin)
```

---

## Security Considerations

### Trust Boundary

Plugins run in the same process as your application. Only install plugins
from trusted sources.

### Validation

MikiUI validates every plugin before registration:

1. **Manifest check** — name, version, and capabilities are verified.
2. **AST vetting** — source code is scanned for dangerous patterns
   (``subprocess``, ``eval``, ``os.system``, etc.).
3. **Import scanning** — only allow-listed modules may be imported.

Plugins that fail validation raise ``PluginSecurityViolation`` and are not
registered.

### Configuring the security policy

```python
from mikiui.app import MikiApp, PluginSecurityConfig

app = MikiApp()
app.set_plugin_security_config(
    PluginSecurityConfig(
        vet_ast=True,
        blocked_capabilities=["filesystem:write"],
        allow_untrusted=False,
    )
)
```

### Sandboxing

MikiUI does not currently execute plugins in a separate OS-level sandbox.
Plugins share the full Python runtime.  The AST vetter and import allow-list
provide **static** sandboxing; for stronger isolation, run untrusted plugins
in a separate process or container.

### Input Validation

Validate all external input in `on_request` and `on_render`:

```python
def on_request(self, request):
    if not is_valid(request.headers.get("X-Api-Key")):
        raise HTTPException(status_code=403)
    return request
```

### Resource Limits

Keep `on_render` and `on_request` fast. Heavy work should be deferred or
cached:

```python
import functools

@functools.lru_cache(maxsize=128)
def expensive_lookup(key):
    return compute(key)
```

### Async Hooks

Use `await` in `on_request` for async I/O:

```python
async def on_request(self, request):
    data = await fetch_external_data()
    request.state.data = data
    return request
```

---

## Plugin Template

Copy this template to start a new plugin:

```python
from mikiui import Plugin, Theme, ThemePlugin, ComponentPlugin, WidgetPlugin

class MyFeaturePlugin(Plugin):
    """Brief description."""

    name = "my-feature"
    depends_on: list[str] = []

    def configure(self, config: dict) -> None:
        self.config = config

    def register(self, app) -> None:
        # Initialize themes, components, widgets
        pass

    def on_render(self, tree) -> Any:
        return tree

    def on_request(self, request) -> None:
        pass

    def on_route_add(self, path, methods, handler) -> None:
        pass

    def on_error(self, error, request) -> None:
        pass

    def on_shutdown(self) -> None:
        pass

# Usage
app = MikiApp()
app.use(MyFeaturePlugin(), config={"option": True})
```
