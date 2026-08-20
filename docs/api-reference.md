# API Reference

This page documents the public API surface of MikiUI. It is organized by
module: app, components, widgets, router, backend, and build.

## Table of Contents

- [`MikiApp`](#mikiapp)
- [`Plugin` System](#plugin-system)
- [`Router`](#router)
- [Components](#components)
- [Widgets](#widgets)
- [Backend (`create_app`)](#backend-create_app)
- [Build Functions](#build-functions)

---

## `MikiApp`

The central application object. Create one instance per app, register routes,
themes, and plugins, then run it.

### Constructor

```python
app = MikiApp(
    title="MikiUI App",
    lang="en",
    favicon=None,
    desktop_icon=None,
    splash_screen=None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | `str` | `"MikiUI App"` | Global page title |
| `lang` | `str` | `"en"` | HTML `lang` attribute |
| `favicon` | `str \| None` | `None` | Favicon path |
| `desktop_icon` | `str \| None` | `None` | Desktop window icon path |
| `splash_screen` | `str \| None` | `None` | Splash screen image URL |

### Routing

```python
@app.route("/")
def home():
    return Div("Home")
```

**Signature:**

```python
def route(
    self,
    path: str,
    methods: tuple[str, ...] = ("GET",),
    name: str | None = None,
    title: str | None = None,
    requires_auth: bool = False,
) -> Callable[[Callable], Callable]
```

Convenience shortcuts:

```python
def get(self, path, name=None, title=None)
def post(self, path, name=None, title=None)
```

### Path Parameters

```python
@app.route("/users/{user_id}")
def show_user(ctx, user_id):
    return Div(f"User {user_id}")
```

### Mounting Routers

```python
from mikiui.router import Router

router = Router(prefix="/admin")
@app.get("/dashboard")
def admin_home():
    return Div("Admin Dashboard")

app.mount(router)
```

### Themes

```python
app.set_theme("light")          # activate a registered theme
app.register_theme(theme_obj)   # register a custom theme
app.set_favicon("/icon.png")    # set favicon
```

### Head Extras

```python
app.set_head_meta("description", "My app")
app.add_head_link("/static/custom.css", rel="stylesheet")
app.add_head_script("/static/app.js", type="module")
```

### Static Files

```python
# Mount an arbitrary directory for static serving
app.mount_static("/uploads", "./uploads")

# Resolve a framework asset URL
url = app.asset_url("components", "splitview", "splitview.css")
# -> "/_miki/components/splitview/static/splitview.css"
```

**`mount_static` signature:**

```python
def mount_static(self, url_path: str, directory: str, *, name: str | None = None) -> MikiApp
```

Mounts *directory* under *url_path*. The directory is served automatically when
the app is built or run. Raises `NotADirectoryError` if the path does not exist.

**`asset_url` signature:**

```python
def asset_url(self, package_type: str, package_name: str, filename: str) -> str
```

Build the URL for a static asset served by the framework. `package_type` is one
of `"components"`, `"widgets"`, `"plugins"`, or `"themes"`.

### Styling Framework

```python
app.set_style_framework("tailwind", mode="local", daisyui=True)
app.set_style_framework("plain")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `framework` | `str` | `"plain"` | `"plain"` or `"tailwind"` |
| `mode` | `str` | `"cdn"` | Tailwind only: `"cdn"` or `"local"` |
| `daisyui` | `bool` | `False` | Tailwind only: enable DaisyUI |

### Plugins

```python
app.use(MyPlugin())             # register a plugin
app.set_plugin_security_config(config)  # set security policy
app.get_plugin_security_config()        # get current policy
```

### Plugin Security API

```python
from mikiui.app import (
    PluginSecurityConfig,
    PluginSecurityViolation,
    PluginValidator,
    validate_plugin,
    load_manifest,
)

# Configure security policy
config = PluginSecurityConfig(
    allow_untrusted=False,      # only builtin/entry-point plugins
    allowed_imports=[],         # empty = default safe list
    blocked_imports=["subprocess"],  # always blocked
    blocked_capabilities=["filesystem:write"],
    allow_filesystem_write=False,
    allow_network=True,
    vet_ast=True,               # scan source for dangerous patterns
    max_plugin_size_bytes=0,    # 0 = no limit
)

app.set_plugin_security_config(config)

# Manual validation
validate_plugin(plugin, config=config)

# Load manifest from module
manifest = load_manifest(module)
```

### Plugin Manifest Schema

```python
from mikiui.app.plugin_security import PluginManifest

manifest = PluginManifest(
    name="my-plugin",
    version="1.0.0",
    description="...",
    author="...",
    license="MIT",
    min_mikiui_version="0.1.0",
    dependencies=[],
    capabilities=["ui:render"],
    homepage="...",
    repository="...",
    source="builtin",  # "builtin" | "local" | "entry_point" | "marketplace"
    checksum="...",
)
```

Plugins can expose their manifest as:
1. Module-level `PLUGIN_MANIFEST` dict
2. `plugin.json` next to the module file
3. Module attributes (`__name__`, `__version__`, `__doc__`) as fallback

### Running

```python
app.run(host="0.0.0.0", port=8000)          # web server
app.run(desktop=True)                        # native window
app.run(host="0.0.0.0", port=8000, reload=True)  # dev with reload
```

### Other Methods

```python
app.url_for("route_name", user_id=42)   # reverse URL resolution
app.get_route("/path")                   # get RouteDef by path
app.shutdown()                           # call plugin shutdown hooks
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `app.state` | `AppState` | Shared dict-like server-side state |
| `app.plugins` | `list[Plugin]` | Registered plugins |
| `app.routes` | `dict[str, RouteDef]` | Registered routes |
| `app.theme` | `str` | Active theme name |
| `app.title` | `str` | Global page title |
| `app.lang` | `str` | HTML language attribute |
| `app.style_framework` | `str` | Active styling framework (`"plain"` or `"tailwind"`) |
| `app.style_mode` | `str` | Tailwind mode (`"cdn"` or `"local"`) |
| `app.style_daisyui` | `bool` | Whether DaisyUI is enabled |

---

## Plugin System

### Base `Plugin`

```python
from mikiui import Plugin

class MyPlugin(Plugin):
    name = "my-plugin"
    depends_on: list[str] = []   # optional: list plugin names this depends on

    def configure(self, config: dict) -> None:
        """Called before register with config dict."""
        pass

    def register(self, app) -> None:
        """Called once by app.use(plugin)."""
        pass

    def on_render(self, tree) -> Any:
        """Post-process component tree before rendering. Return modified tree."""
        return tree

    def on_request(self, request) -> None:
        """Called for every incoming request."""
        pass

    def on_route_add(self, path, methods, handler) -> None:
        """Called when a route is registered."""
        pass

    def on_error(self, error, request) -> None:
        """Called when a route handler raises."""
        pass

    def on_shutdown(self) -> None:
        """Called when the app shuts down."""
        pass

    def assets(self) -> list[str]:
        """Return list of static asset paths to bundle."""
        return []

    def backend_routes(self) -> list[dict]:
        """Return FastAPI route definitions to mount."""
        return []

    def middleware_classes(self) -> list[type]:
        """Return FastAPI middleware classes."""
        return []
```

### `ThemePlugin`

```python
from mikiui import ThemePlugin, Theme

class DarkMod(ThemePlugin):
    name = "dark-mod"

    def theme(self) -> Theme:
        return Theme(
            name="dark-mod",
            source="plugin",
            css_path="/path/to/dark.css",
            extra_classes=["data-theme-dark-mod"],
            variables={"--miki-primary": "#8b5cf6"},
        )

app.use(DarkMod())
app.set_theme("dark-mod")
```

### `ComponentPlugin`

```python
from mikiui import ComponentPlugin
from mikiui.components import Component

class StarRating(Component):
    tag = "span"
    def __init__(self, value, **attrs):
        super().__init__("★" * value, **attrs)

class MyComponents(ComponentPlugin):
    name = "my-components"

    def components(self) -> dict[str, type]:
        return {"StarRating": StarRating}

app.use(MyComponents())
```

### `WidgetPlugin`

```python
from mikiui import WidgetPlugin

class SearchWidget:
    def render(self):
        from mikiui import Div, Input
        return Div(Input(placeholder="Search..."))

class MyWidgets(WidgetPlugin):
    name = "my-widgets"

    def widgets(self) -> dict[str, type]:
        return {"Search": SearchWidget}

app.use(MyWidgets())
```

### Plugin Discovery (Entry Points)

Plugins can be auto-discovered via setuptools entry points:

```toml
[project.entry-points."mikiui.plugins"]
dark_mod = "my_package.plugin:DarkModPlugin"
```

Install with `pip install my-package` and the plugin is available.

### Marketplace API

```python
from mikiui.app import (
    DirectoryIndexSource,
    PyPIIndexSource,
    PluginMarketplace,
    PluginSecurityConfig,
)

# Local directory index
source = DirectoryIndexSource("mikiui_plugins")
market = PluginMarketplace(source)

# Search
results = market.search("chart")
for info in results:
    print(info.name, info.version, info.description)

# Install
app.set_plugin_security_config(PluginSecurityConfig(allow_untrusted=True))
plugin = market.install("chart-widget", app)

# Bulk install
installed = market.install_all(app)
```

---

## Router

### `Router`

Group routes under a common prefix.

```python
from mikiui.router import Router

router = Router(prefix="/api/v1")

@router.get("/items")
def list_items(ctx):
    return Div("Items")

# Mount on the app
app.mount(router)
```

**Constructor:**

```python
Router(prefix: str = "")
```

**Methods:**

```python
router.get(path, name=None, title=None, requires_auth=False)
router.post(path, name=None, title=None, requires_auth=False)
router.add(path, methods=("GET",), name=None, title=None, requires_auth=False)
router.mount(target)  # target: MikiApp or Router
```

### PWA Manifest

```python
from mikiui.router import add_pwa_manifest

add_pwa_manifest(
    app_fastapi,
    name="My App",
    icon="/icon.png",
    start_url="/",
    display="standalone",
)
```

---

## Components

All components live in `mikiui.components` and inherit from `Component`.

### Base `Component`

```python
from mikiui.components import Component

class MyComponent(Component):
    tag = "div"   # HTML tag to render

    def __init__(self, *children, **attrs):
        super().__init__(*children, **attrs)
```

Positional arguments become child nodes. Keyword arguments become HTML
attributes (with `_` → `-` conversion, e.g. `class_` → `class`).

### HTML Elements

Import from `mikiui.components`:

```python
from mikiui.components import (
    # Structure
    Html, Head, Body, Div, Section, Article, Aside, Header, Footer, Main, Nav,
    # Text
    H1, H2, H3, H4, H5, H6, Heading, P, Paragraph, Span, Br, Hr,
    # Semantic
    Blockquote, Pre, Preformatted, Code, Mark, Small, Strong, Em, Emphasis,
    Abbr, Abbreviation, Address, Time, Kbd, Keyboard, Var, Variable, Samp, Sample, Cite, Citation,
    # Media
    Img, Image, Video, Audio, Canvas, Svg, SVG, Picture, Source, Figure, Figcaption,
    # Lists
    Ul, Ol, Li, Dl, Dt, Dd, UnorderedList, OrderedList, ListItem,
    DescriptionList, DescriptionTerm, DescriptionDetail,
    # Forms
    Form, Input, Textarea, Select, Option, Optgroup, Button, Label,
    Fieldset, Legend, Checkbox, Radio, Slider, Switch, Upload,
    # Data
    Table, Caption, Thead, Tbody, Tfoot, Tr, Th, Td,
    # Interactive
    Dialog, Modal, Details, Summary, DialogTitle, DialogBody, DialogFooter,
    # Navigation
    A, Anchor, Menu, MenuItem, Breadcrumbs,
    # Misc
    Link, Meta, Script, Style, Title,
)
```

**Catalog aliases:** Short-form names like `P` (`<p>`) and long-form aliases like
`Paragraph` are both available and point to the same class. This applies to:
`P`/`Paragraph`, `Img`/`Image`, `A`/`Anchor`, `Pre`/`Preformatted`, `Em`/`Emphasis`,
`Abbr`/`Abbreviation`, `Cite`/`Citation`, `Kbd`/`Keyboard`, `Var`/`Variable`,
`Samp`/`Sample`, `Svg`/`SVG`, `Ul`/`UnorderedList`, `Ol`/`OrderedList`, `Li`/`ListItem`,
`Dl`/`DescriptionList`, `Dt`/`DescriptionTerm`, `Dd`/`DescriptionDetail`.

### `Heading`

The `Heading` component dynamically selects the HTML tag based on the `level` parameter:

```python
from mikiui.components import Heading

Heading("Section Title", level=2)  # renders as <h2>Section Title</h2>
```

### `RawHtml`

A low-level escape hatch for trusted HTML content. Use with caution — the
caller is responsible for ensuring content is safe. Used internally by
`Chart` for inline SVG, and by icon components.

```python
from mikiui import RawHtml
RawHtml('<rect width="10" height="10" />').to_html()
# '<rect width="10" height="10" />'
```

### Common Component Signatures

**`Button`**

```python
Button(
    *children,
    variant="primary",       # primary | secondary | ghost | danger | success | warning | link | outline | text
    size="md",               # xs | sm | md | lg | xl
    loading=False,
    block=False,
    icon=None,
    icon_position="left",
    **attrs,
)
```

Class methods: `Button.group(*buttons)`, `Button.icon_button(icon, aria_label)`,
`Button.toggle(icon_on, icon_off, aria_label_on, aria_label_off, *, pressed=True)`,
`SubmitButton()`, `IconButton(icon, aria_label)`.

The `Button.toggle` class method creates a toggle button with two icon states.
The `pressed` keyword (default `True`) sets the initial toggle state and is
reflected in `aria-pressed` and `data-miki-state` for accessibility.

**`Input`**

```python
Input(
    *children,
    type="text",
    variant="default",       # default | filled | text
    size="md",               # sm | md | lg
    state="default",         # default | valid | invalid | warning
    loading=False,
    disabled=False,
    **attrs,
)
```

Variants: `Textarea`, `Checkbox`, `Radio`, `Slider`, `Switch`, `Select`,
`Upload`.

**`Form`**

```python
Form(
    *children,
    layout="vertical",       # vertical | inline
    **attrs,
)
```

**`Dialog`**

```python
Dialog(
    *children,
    open=False,
    title=None,
    size="md",               # xs | sm | md | lg | xl | fullscreen
    close_on_overlay=True,
    close_on_escape=True,
    **attrs,
)
```

**`Table`**

```python
Table(
    *children,
    variant="default",       # default | striped
    **attrs,
)
```

### Component Decorator

```python
from mikiui.components import component

@component
def MySpan():
    return Span("Hello")
```

---

## Widgets

Widgets are high-level composite components built from base components.

### Layout Widgets

**`Hero`**

```python
Hero(
    title,
    subtitle=None,
    image=None,
    action=None,
    variant="primary",
    align="left",
    **attrs,
)
```

**`Footer`**

```python
Footer(
    *content,
    copyright=None,
    social=None,  # list of (label, href) tuples
    **attrs,
)
```

**`Sidebar`**

```python
Sidebar(
    *items,           # (label, href) tuples or Components
    title=None,
    width="250px",
    mobile=False,
    **attrs,
)
```

### Data & Media

**`DataGrid`**

```python
DataGrid(
    columns,           # list[str] or list[tuple]
    rows,              # list[dict] or list[list]
    sortable=True,
    filterable=False,
    pagination=True,
    search=True,
    page=0,
    page_size=10,
    height=None,
    **attrs,
)
```

**`Chart`**

```python
Chart(
    series=[10, 20, 30],    # list of numeric values
    kind="bar",             # line | bar | pie (default: "bar")
    width=320,              # SVG viewport width in px
    height=160,             # SVG viewport height in px
    class_=None,            # additional CSS classes
    **attrs,
)
```

The SVG content inside `Chart` is rendered using `RawHtml` to prevent HTML escaping.
If `series` is empty, renders a placeholder `(no data)` message with role `"img"`
and `aria-label="Chart"` for accessibility.

**`MediaPlayer`**

```python
MediaPlayer(
    kind="audio",      # audio | video
    src="https://...",
    **attrs,
)
```

**`Carousel`**

```python
Carousel(
    *slides,           # (image_url, caption) tuples
    autoplay=False,
    interval=3000,
    **attrs,
)
```

### Panels

**`DockablePanel`**

```python
DockablePanel(
    title,
    *content,
    closable=True,
    floatable=True,
    **attrs,
)
```

**`SplitView`** *(widgets)*

```python
SplitView(
    left,
    right,
    is_horizontal=True,
    **attrs,
)
```

A 2-pane resizable layout splitter (widget-level). Note: the editor-area
component `EditorArea` (formerly `SplitView` in `components/splitview/`)
is a separate, VS Code-like multi-tab editor. Both are intentionally named
differently to avoid the previous name collision.

**`TabbedPanel`**

```python
TabbedPanel(
    *tabs,   # (label, content) tuples
    **attrs,
)
```

**`CollapsiblePanel`**

```python
CollapsiblePanel(
    title,
    *content,
    open=False,
    **attrs,
)
```

### Auth

**`LoginForm`**

```python
LoginForm(
    action="/login",
    method="post",
    **attrs,
)
```

**`SignupForm`**

```python
SignupForm(
    action="/signup",
    method="post",
    **attrs,
)
```

### Other Widgets

| Widget | Purpose |
|--------|---------|
| `Avatar` | User avatar with status indicator |
| `Badge` | Small status label |
| `Progress` | Progress bar |
| `Card` | Paper-like container |
| `Pagination` | Page navigation controls |
| `Drawer` | Slide-in panel |
| `Rail` | Slim icon navigation rail |
| `ContextWindow` | Floating context menu |
| `ChatUI` | Messaging interface |
| `Dashboard` | Dashboard layout |
| `DatePicker` | Date input |
| `ColorPicker` | Color input |
| `Dial` | Circular dial control |
| `LCDNumber` | Digital number display |
| `LogViewer` | Log display with auto-scroll |
| `TerminalWidget` | Embedded terminal |
| `FilePicker` | File browser |
| `KanbanBoard` | Kanban task board |
| `IDEEditor` | Code editor with syntax highlighting |
| `InspectorPanel` | Debugging state/routes panel |
| `PropertyGrid` | Editable property/value pairs |
| `ScrollPanel` | Scrollable content area |
| `ToolboxPanel` | Collapsible toolbox |
| `GroupBox` | Styled titled container |
| `ProgressDialog` | Modal progress dialog |
| `MdiArea` | Multi-document interface area |
| `MdiSubWindow` | Sub-window inside MDI area |
| `MenuBar` | Menu bar |
| `StatusBar` | Status bar |
| `SplashScreen` | Splash screen widget |
| `StackedPanel` | Stacked panel container |
| `SidePanel` | Slide-in side panel |
| `StreamingPanel` | Live data/video stream |
| `NotificationPanel` | Toasts and alerts |
| `FormWizard` | Multi-step form |
| `SearchPanel` | Search bar + filters + results |

---

## Backend (`create_app`)

```python
from mikiui.backend import create_app

fastapi_app = create_app(
    miki_app,
    runtime="local",         # "local" (offline) or "cdn"
    cors_origins=None,       # list of allowed origins, or ["*"] for dev
)
```

Returns a **FastAPI** application that can be run with uvicorn:

```python
import uvicorn

uvicorn.run(create_app(app), host="0.0.0.0", port=8000)
```

The backend automatically:

- Mounts static runtime assets under `/_miki/runtime`
- Registers all MikiUI routes as FastAPI endpoints
- Adds default security middleware (CSP, HSTS, etc.)
- Serves a PWA manifest at `/manifest.webmanifest`

### WebSocket

```python
from mikiui.backend import ConnectionManager, mount_websocket

manager = ConnectionManager()
mount_websocket(app_fastapi, manager, "/ws")
```

### SSE

```python
from mikiui.backend import sse_response

@app_fastapi.get("/stream")
async def stream():
    return sse_response(generate_events())
```

---

## Build Functions

### `build_web`

```python
from mikiui.build import build_web

report = build_web(
    app,
    mode="fullstack",       # "fullstack" or "separate"
    out_dir="dist",
    theme=None,             # "tailwind", "light", etc.
    daisyui=False,
    tailwind_ext=None,
    tailwind_content=None,
    skip_tailwind=False,
)
```

**Report keys:** `target`, `mode`, `out_dir`, `pages`, `runtime_assets`,
`manifest`, `shell`, `csp_nonce`, `server_script`, `tailwind_built`,
`status`.

### `build_desktop`

```python
from mikiui.build import build_desktop

report = build_desktop(
    app,
    out_dir="dist_desktop",
    app_spec=None,          # "module:attr" spec
    icon=None,
    onefile=False,
)
```

**Report keys:** `status`, `out_dir`, `platform`, `web_build_dir`,
`launcher`, `spec`, `executable_name`, `app_spec`.

### `run_desktop`

```python
from mikiui.build import run_desktop

run_desktop(
    app,
    host="127.0.0.1",
    port=8000,
    title=None,
    width=1024,
    height=720,
    runtime="local",
    native=True,
    reload=False,
    app_spec=None,
    icon=None,
)
```

### `optimize`

```python
from mikiui.build import optimize

result = optimize(
    asset_paths=["dist/_miki/runtime/htmx.min.js", "dist/_miki/runtime/miki.css"],
    level="balanced",       # "none" | "balanced" | "aggressive"
)
# {"optimized": 2, "skipped": 0}
```

### `build_css` (Tailwind)

```python
from mikiui.build import build_css

css_path = build_css(
    theme="light",
    daisyui=False,
    out="mikiui/runtime/themes/tailwind.css",
    optimize=True,
    watch=False,
)
```
