# MikiUI Router Guide

The `Router` class lets you organize route handlers into separate files and mount
them under URL prefixes — similar to FastAPI's `APIRouter`.

## Quick Start

```python
# app.py
from mikiui import MikiApp, Div
from mikiui.router import Router

app = MikiApp(title="My App")

@app.route("/")
def home():
    return Div("Welcome")

# Mount a router with all its routes under /users
app.mount(router)

if __name__ == "__main__":
    app.run()
```

## Separate Route Files

Create route files that define routers, then import and mount them in your main
app:

```python
# routes/users.py
from mikiui.router import Router
from mikiui import Div

router = Router(prefix="/users")

@router.get("/")
def list_users():
    return Div("User List")

@router.get("/profile")
def profile():
    return Div("Profile Page")

@router.post("/create")
def create_user():
    return Div("User Created")
```

```python
# app.py
from mikiui import MikiApp
from routes.users import router as user_router

app = MikiApp()
app.mount(user_router)

if __name__ == "__main__":
    app.run()
```

## Two Usage Patterns

### 1. Explicit (no mount needed)

Pass the app as the first argument to each decorator:

```python
router = Router(prefix="/admin")

@router.get(app, "/dashboard")
def admin_dashboard():
    return Div("Admin Dashboard")
```

### 2. Mounted (bare decorators)

Mount the router first, then use bare decorators:

```python
router = Router(prefix="/admin")
app.mount(router)

@router.get("/dashboard")
def admin_dashboard():
    return Div("Admin Dashboard")
```

Both patterns produce identical route entries in `app.routes`.

## Multiple Routers

Mount multiple routers for different sections of your app:

```python
user_router = Router(prefix="/users")
admin_router = Router(prefix="/admin")

app.mount(user_router)
app.mount(admin_router)

@user_router.get("/list")
def users():
    return Div("Users")

@admin_router.get("/panel")
def admin():
    return Div("Admin Panel")
```

## Path Parameters

Route handlers can accept path parameters using FastAPI-style `{param}` syntax:

```python
@app.route("/users/{user_id}")
def show_user(ctx, user_id: str):
    return Div(f"User {user_id}")
```

When the first parameter is named `ctx` or `request`, path params are passed as
keyword arguments alongside `ctx`. Without a ctx parameter, path params are
passed directly:

```python
@app.route("/items/{item_id}")
def item(item_id: str):
    return Div(f"Item {item_id}")
```

## Query Parameters and Form Data

Access query params via `ctx.query_params` (requires a `ctx` parameter):

```python
@app.route("/search")
def search(ctx):
    q = ctx.query_params.get("q", "")
    return Div(f"Results for: {q}")
```

For form data, use `await ctx.form()`:

```python
@app.post("/login")
async def login(ctx):
    data = await ctx.form()
    username = data.get("username", "")
    return Div(f"Welcome, {username}!")
```

## Title Support

Pass a `title` parameter for per-page `<title>` tags:

```python
@router.get("/dashboard", title="Admin Dashboard")
def dashboard():
    return Div("Dashboard")
```

Title resolution priority (highest first):
1. Handler sets `ctx.meta["title"]`
2. `title` parameter on the route
3. App's global `title`

## API Reference

### Router

```python
class Router(prefix=..., app=None)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `prefix` | `str` | URL prefix for all routes (default: `""`) |
| `app` | `MikiApp \| None` | Pre-bind to an app (optional) |

**Methods:**
- `router.get(app?, path, name?, title?)` — register a GET handler
- `router.post(app?, path, name?, title?)` — register a POST handler
- `router.route(app?, path, methods, name?, title?)` — register with custom methods
- `router.add(app?, path, methods, name?, title?)` — low-level registration
- `router.mount(app)` — bind router to an app (called by `app.mount(router)`)

### MikiApp.mount

```python
app.mount(router, *, prefix=None)
```

Mounts a `Router` onto the app. After mounting, the router's decorators can be
used in bare form.

| Parameter | Type | Description |
|-----------|------|-------------|
| `router` | `Router` | The router to mount |
| `prefix` | `str \| None` | Override the router's prefix |
