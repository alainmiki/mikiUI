# MikiUI Project Plan

## Vision
MikiUI is a Python-first UI framework that allows developers to build user interfaces and run them as standalone GUIs or convert them into websites. It emphasizes simplicity, optimistic UI, and lightweight builds.

## Core Principles
- Python-first, beginner-friendly (usable with 2 weeks of Python knowledge).
- UI optimistic: partial updates by default, full HTML only on route changes.
- Lightweight builds optimized for small file sizes.
- Plugin ecosystem with marketplace.
- Full parity with PyQt components and advanced widgets from VS UI.

## Tech Stack
- **Backend**: FastAPI (routes, WebSocket, SSE).
- **Frontend Runtime**: HTMX + Alpine.js (DOM updates, interactivity).
- **Styling**: TailwindCSS (default), Bootstrap (optional).
- **Packaging**: 
  - **Fullstack mode**: FastAPI serves both frontend and backend together.  
  - **Separate mode**: Frontend packaged independently, backend runs standalone.  
- **Database (optional)**: PostgreSQL/Redis for state persistence.
- **Testing**: Pytest + Playwright.
- **CLI Tooling**: Click/Typer for `mikiui` commands.
- **DevTools**: Browser extension for state/routes inspection.

## Modules
- Components → Python classes mapped to HTML/Tailwind/Bootstrap (all HTML elements including dialogs).
- Widgets → High-level composite components (DataGrid, MediaPlayer, Dashboard, Panels).
- App → User-facing API (routing, state, plugin use).
- Engine → Rendering, diffing, optimistic updates.
- Runtime → Swappable JS runtime (HTMX/Alpine).
- Router → Multi-page, SPA, PWA-ready.
- Build → Packaging, optimization, desktop/web.
- Plugin → Plugin loader + marketplace.
- Media → Streaming, recording, EQ, filters.

## API Design Examples

### Routing
```python
@app.route("/")
def home():
    return Button("Click me!", onclick="alert('Hello!')")

@app.route("/about")
def about():
    return Dialog("About MikiUI", content="This is a dialog example")
```
### State management
```python
app.state["count"] = 0

@app.route("/counter")
def counter():
    return Button(f"Count: {app.state['count']}", onclick="increment()")

```

### component
```python
Form([
    Input(type="text", placeholder="Username"),
    Input(type="password", placeholder="Password"),
    Button("Login", onclick="submitLogin()"),
    Dialog("Terms", content="Please accept terms before continuing")
])
```

### widget
```python
from mikiui.widgets import DataGrid, MediaPlayer

@app.route("/users")
def users():
    return DataGrid(data=fetch_users(), columns=["Name", "Email", "Role"])

@app.route("/music")
def music():
    return MediaPlayer(source="song.mp3", eq="bass_boost")
```

### plugin
```python
from mikiui.plugins import AuthPlugin
app.use(AuthPlugin())

```
### Build
```bash
mikiui new myapp
mikiui dev
mikiui build --target web --mode fullstack
mikiui build --target desktop
```