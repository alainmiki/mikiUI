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

## Nested Routers

Routers can be mounted on other routers. The child inherits the parent's prefix:

```python
api = Router(prefix="/api")
v1 = Router(prefix="/v1")
api.mount(v1)

@v1.get("/items")
def items():
    return Div("items")  # mounted at /api/v1/items
```

Nested router prefixes are computed from the parent chain. The child's prefix is
not mutated; reusing the same router instance across apps is safe.

## Route Name Uniqueness

Route names default to the handler function name. Duplicate names raise
`ValueError`:

```python
@app.route("/home")
def home():
    return Div("Home")

@app.route("/about")
def home():  # ValueError: route name 'home' is already used
    return Div("About")
```

Pass a unique `name=` to avoid collisions:

```python
@app.route("/about", name="about_page")
def home():
    return Div("About")
```

## Route Groups

Group routes that share a prefix, auth, and middleware:

```python
from mikiui.router.auth import AuthRequirement
from mikiui.router.csrf import CSRFMiddleware
from mikiui.router.rate_limit import RateLimitMiddleware

api = app.route_group("/api")
api.auth(AuthRequirement(strategy="jwt", scopes=["user"]))
api.rate_limit(limit=200, window=60)
api.use(RequestLoggingMiddleware)

@api.get("/profile")
def profile(ctx):
    return Div("Your profile")

@api.post("/logout")
def logout(ctx):
    return Div("Logged out")
```

### Route group methods

| Method | Description |
|--------|-------------|
| `group.auth(requirement)` | Set auth requirement for all routes in the group |
| `group.rate_limit(limit, window)` | Enable rate limiting |
| `group.csrf(exempt_paths, exempt_methods)` | Enable CSRF protection |
| `group.use(middleware_cls)` | Add middleware class |
| `group.get/post/route(path, **kwargs)` | Register a handler (prefix is auto-applied) |

### Per-route overrides

Override group settings on individual routes:

```python
public_api = app.route_group("/api/public")
public_api.auth(AuthRequirement(strategy="session"))

@public_api.get("/health", auth=AuthRequirement(strategy="none"))
def health():
    return Div("OK")
```

## Custom 404 Handler

```python
@app.not_found
def not_found(ctx):
    return Div("This page does not exist.")
```

## Custom Error Pages

```python
app.set_error_page(403, lambda ctx: Div("Access denied"))
app.set_error_page(500, lambda ctx: Div("Something went wrong"))
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

## Async Handlers

Both sync and async handlers are supported.  Use `async def` when you need to
perform asynchronous operations (database queries, API calls, etc.):

```python
@app.route("/async-users/{user_id}")
async def get_user(ctx, user_id: str):
    user = await fetch_user(user_id)
    return Div(f"User: {user.name}")
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
class Router(prefix=...)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `prefix` | `str` | URL prefix for all routes (default: `""`) |

**Methods:**
- `router.get(path_or_app, path?, name?, title?)` — register a GET handler
- `router.post(path_or_app, path?, name?, title?)` — register a POST handler
- `router.route(path_or_app, path?, methods, name?, title?)` — register with custom methods
- `router.add(path_or_app, path?, methods, name?, title?)` — low-level registration
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
