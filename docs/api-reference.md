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

### Plugins

```python
app.use(MyPlugin())             # register a plugin
```

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
    H1, H2, H3, H4, H5, H6, P, Span, Br, Hr,
    # Semantic
    Blockquote, Pre, Code, Mark, Small, Strong, Em, Abbr, Address,
    Time, Kbd, Var, Samp, Cite,
    # Media
    Img, Video, Audio, Canvas, Svg, Picture, Source, Figure, Figcaption,
    # Lists
    Ul, Ol, Li, Dl, Dt, Dd,
    # Forms
    Form, Input, Textarea, Select, Option, Optgroup, Button, Label,
    Fieldset, Legend, Checkbox, Radio, Slider, Switch, Upload,
    # Data
    Table, Caption, Thead, Tbody, Tfoot, Tr, Th, Td,
    # Interactive
    Dialog, Modal, Details, Summary, DialogTitle, DialogBody, DialogFooter,
    # Navigation
    A, Menu, MenuItem, Breadcrumbs,
    # Misc
    Link, Meta, Script, Style, Title,
)
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
`SubmitButton()`, `IconButton(icon, aria_label)`.

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
    type="line",       # line | bar | pie
    data=[10, 20, 30],
    labels=["A", "B", "C"],
    **attrs,
)
```

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

**`SplitView`**

```python
SplitView(
    left,
    right,
    is_horizontal=True,
    **attrs,
)
```

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
