# API Reference

This page documents the public API surface of MikiUI. It is organized by module: app, components, widgets, router, backend, and build.

## MikiApp

The central application object. Create one instance per app, register routes, themes, and plugins, then run it.

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
    auth: AuthRequirement | None = None,
    rate_limit: RateLimitConfig | None = None,
    summary: str | None = None,
    description: str | None = None,
    tags: list[str] | None = None,
) -> Callable
```

### Themes

```python
app.set_theme("dark")
app.set_style_framework("tailwind", mode="cdn", daisyui=True)
```

### Plugins

```python
app.use(plugin)
app.set_plugin_security_config(config)
```

### Static Files

```python
app.mount_static("/static", "./static")
url = app.asset_url("components", "button", "button.css")
```

### Testing

```python
client = app.test_client()
response = client.get("/")
```

## Router

```python
from mikiui.router import Router

router = Router(prefix="/users")
```

**Methods:**
- `router.get(path, **kwargs)` — register a GET handler
- `router.post(path, **kwargs)` — register a POST handler
- `router.route(path, methods, **kwargs)` — register with custom methods
- `router.mount(app)` — bind router to an app

## Backend (`create_app`)

```python
from mikiui.backend import create_app

fastapi_app = create_app(
    miki_app,
    runtime="local",
    cors_origins=None,
    enable_csrf=True,
)
```

Returns a FastAPI app with:
- All routes registered
- Static file mounting
- Middleware (CORS, CSRF, rate limiting, security headers)
- WebSocket support
- OpenAPI docs at `/docs`

## Build Functions

### `build_web`

```python
from mikiui.build import build_web

report = build_web(
    app,
    mode="fullstack",       # "fullstack" or "separate"
    out_dir="dist",
    theme=None,
    framework=None,
    style_mode="cdn",
    daisyui=False,
    skip_tailwind=False,
)
```

**Report keys:** `target`, `mode`, `out_dir`, `pages`, `runtime_assets`, `manifest`, `shell`, `sitemap`, `robots`, `404`, `csp_nonce`, `server_script`, `tailwind_built`, `skipped_routes`, `parameterized_pages`, `route_manifest_used`, `status`.

### `build_desktop`

```python
from mikiui.build import build_desktop

report = build_desktop(
    app,
    out_dir="dist_desktop",
    app_spec=None,
    icon=None,
    onefile=False,
)
```

**Report keys:** `status`, `out_dir`, `platform`, `web_build_dir`, `launcher`, `spec`, `bundle`, `warning`, `executable_name`, `app_spec`.

## Components

All HTML elements are available as Python classes. See [Components Guide](../guide/components.md) for the full catalog.

## Widgets

High-level composite UI components. See [Widgets Guide](../guide/widgets.md) for the full catalog.
