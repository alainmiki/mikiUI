<div align="center">

# MikiUI

**Build beautiful web and desktop apps — entirely in Python.**

[![PyPI version](https://img.shields.io/pypi/v/mikiui)](https://pypi.org/project/mikiui/)
[![Python](https://img.shields.io/pypi/pyversions/mikiui)](https://pypi.org/project/mikiui/)
[![License](https://img.shields.io/pypi/l/mikiui)](LICENSE)

[Installation](#installation) · [Quick Start](#quick-start) · [Documentation](#documentation) · [Examples](#examples)

</div>

---

MikiUI is a Python-first UI framework that lets you build **web applications and native desktop windows** from a single codebase. No JavaScript required for logic — just Python classes that map to HTML, with a modern component API, built-in security, and real-time capabilities.

> **Mobile (PWA)** support is planned for v0.3. The web output is already responsive and mobile-friendly; native mobile wrappers (Capacitor) are on the roadmap.

## Why MikiUI?

- **One codebase, multiple targets** — deploy as a website, a native desktop app (pywebview), or a static site
- **Python-first** — write routes, components, and state in pure Python; the framework handles HTML, CSS, and JS interop
- **60+ components and widgets** — from buttons and forms to data grids, IDE editors, chat UIs, and MDI workspaces
- **Mobile-native apps** — build iOS and Android apps with Capacitor (cloud or on-device backend)
- **Real-time built in** — WebSocket with rooms/channels, SSE, WebRTC signaling, and auth integration
- **Secure by default** — CSRF protection, security headers, CSP nonces, and plugin sandboxing
- **API-ready** — auto-generated OpenAPI docs, type-coerced path params, and route groups
- **Theming** — 4 built-in themes (light, dark, solarized, dracula) with custom theme support
- **Plugin ecosystem** — extend with custom components, widgets, themes, and backend routes
- **Native device features** — camera, geolocation, push notifications, haptics, clipboard, and more

## Installation

### From PyPI (recommended)

```bash
pip install mikiui
```

### With Tailwind CSS support

```bash
pip install mikiui[tailwind]
npm install  # installs Tailwind + DaisyUI
```

### For desktop apps

```bash
pip install mikiui[desktop]
```

### Verify

```bash
mikiui --help
```

---

## Quick Start

### 1. Create a new project

```bash
mikiui new myapp
cd myapp
```

### 2. Write your app

```python
# app.py
from mikiui import MikiApp, Div, H1, P, Button

app = MikiApp(title="My App")

@app.route("/", title="Home")
def home():
    return Div(
        H1("Welcome to MikiUI!"),
        P("Build web and desktop apps in Python."),
        Button("Get Started", class_="miki-btn-primary"),
        class="flex flex-col items-center justify-center h-screen gap-4",
    )

if __name__ == "__main__":
    app.run()           # web server
    # app.run(desktop=True)  # native window
```

### 3. Run it

```bash
mikiui dev            # development server with hot-reload
# or
python app.py         # direct execution
```

Open `http://127.0.0.1:8000` in your browser.

---

## What You Can Build

| Target | Command | Description |
|--------|---------|-------------|
| **Website** | `mikiui dev` | FastAPI + HTMX dev server |
| **Desktop App** | `mikiui desktop` | Native pywebview window |
| **Static Site** | `mikiui build --target web` | Pre-rendered HTML for any host |
| **API Backend** | `create_app(app)` | FastAPI with OpenAPI docs |

---

## Features

### Components & Widgets
All HTML elements as Python classes (`Button`, `Input`, `Form`, `Table`, `Dialog`, `Tabs`) plus high-level widgets (`DataGrid`, `MediaPlayer`, `DockablePanel`, `IDEEditor`, `ChatUI`, `KanbanBoard`, `Calendar`, `Carousel`, and more).

### Routing
Type-coerced path params, route groups, pattern-matched lookup, and per-route auth:

```python
@app.route("/users/{user_id:int}", summary="Get user", tags=["users"])
def get_user(ctx, user_id: int):
    return Div(f"User {user_id}")
```

### Real-Time
WebSocket with rooms, channels, and auth integration:

```python
manager = ConnectionManager()
manager.join_room(ws, "chat-room")
await manager.broadcast_to_room("chat-room", {"message": "Hello!"})
```

### Security
CSRF by default, security headers, CSP nonces, rate limiting, and plugin sandboxing.

### API Documentation
Auto-generated OpenAPI schema with Swagger UI and ReDoc at `/docs` and `/redoc`.

### Theming
4 built-in themes with custom theme support. Switch at runtime:

```python
app.set_theme("dark")
```

### Styling
Tailwind CSS (with optional DaisyUI) or plain CSS — switch without changing app logic.

---

## Commands

| Command | Description |
|---------|-------------|
| `mikiui new <name>` | Scaffold a new project |
| `mikiui dev` | Development server with hot-reload |
| `mikiui desktop` | Native desktop window |
| `mikiui build --target web` | Static web build |
| `mikiui build --target desktop` | Desktop package |
| `mikiui build --target mobile` | Mobile project (Capacitor) |
| `mikiui mobile build` | Build mobile project |
| `mikiui mobile run` | Run on device/emulator |
| `mikiui mobile open` | Open in IDE |
| `mikiui mobile info` | Show mobile config |
| `mikiui mobile doctor` | Check system readiness |
| `mikiui mobile plugins` | List available plugins |
| `mikiui mobile setup` | Interactive setup wizard |
| `mikiui mobile publish` | Prepare for store publishing |
| `mikiui tailwind dev` | Watch & rebuild Tailwind CSS |
| `mikiui install tailwind` | Install Tailwind + npm deps |

---

## Examples

### API with docs
```python
from mikiui import MikiApp
from mikiui.backend import create_app
from mikiui_app_plugins import APIPlugin, SessionPlugin

app = MikiApp(title="My API")
session = SessionPlugin(secret_key="change-me")
app.use(session)
app.use(APIPlugin(title="My API", version="1.0.0", session_plugin=session))

@app.get("/api/items", summary="List items", tags=["items"])
def list_items(ctx):
    return [{"id": 1, "name": "Widget"}]

@app.post("/api/items", summary="Create item", tags=["items"])
def create_item(ctx):
    return {"id": 2, "name": "New Item"}, 201

fastapi_app = create_app(app)
# OpenAPI docs at /docs, ReDoc at /redoc
```

### WebSocket chat with rooms
```python
from mikiui.backend.websocket import ConnectionManager, mount_websocket

manager = ConnectionManager(max_connections_per_user=5)

async def chat_handler(ws, manager):
    user_id = ws.state.mikiui_user_id
    manager.join_room(ws, "general")
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast_to_room("general", {"user": user_id, "text": data})
    except WebSocketDisconnect:
        manager.disconnect(ws)
```

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/getting-started.md) | Installation, first app, CLI reference |
| [Mobile Guide](docs/mobile.md) | Build iOS and Android apps |
| [Mobile Tutorial](docs/mobile-tutorial.md) | Step-by-step photo app tutorial |
| [Mobile Automation](docs/mobile-automation.md) | One-click build, test, sign, publish |
| [API Reference](docs/api-reference.md) | Full method signatures and examples |
| [Widget Catalog](docs/widgets.md) | All 60+ widgets with examples |
| [Router Guide](docs/router-guide.md) | Routing, groups, middleware |
| [Security Guide](docs/security.md) | CSRF, auth, headers, plugin security |
| [Styling Guide](docs/styling.md) | Tailwind, plain CSS, themes |
| [Plugin System](docs/plugins.md) | Creating and publishing plugins |
| [Deployment](docs/deployment.md) | Production setup, static export |
| [Themes](docs/themes.md) | Built-in and custom themes |
| [Changelog](docs/changelog.md) | Version history |

---

## Development Setup (Contributors)

To set up the project for development:

```bash
git clone https://github.com/alainmiki/mikiUI.git
cd mikiUI
pip install -e ".[dev,build,desktop,tailwind]"
pip install pytest-playwright
playwright install --with-deps chromium
```

Run tests:

```bash
python -m pytest tests/ --ignore=tests/e2e    # unit + integration
python -m pytest tests/e2e/                    # browser e2e (needs Chromium)
```

Build and validate:

```bash
python -m build
mikiui build --target web
mikiui build --target desktop
```

---

## Roadmap

| Version | Focus | Status |
|---------|-------|--------|
| v0.2 | Core framework hardening, security, API docs, CLI | ✅ Complete |
| v0.3 | Mobile wrappers (Capacitor), PWA, native bridges | ✅ Complete |
| v0.4 | Plugin marketplace, database/Redis integration | Planned |

---

## Requirements

- **Python 3.14+**
- **Node.js 18+** (only for Tailwind CSS)
- **pywebview** (only for desktop mode, auto-installed with `[desktop]`)

## License

[MIT](LICENSE)
