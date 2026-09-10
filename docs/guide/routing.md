# Routing

MikiUI's routing system lets you organize route handlers into separate files, apply middleware, and define URL patterns with type-coerced parameters.

## Basic Routes

```python
from mikiui import MikiApp, Div

app = MikiApp(title="My App")

@app.route("/")
def home():
    return Div("Home")

@app.route("/about")
def about():
    return Div("About")

@app.route("/users/{user_id}")
def user_profile(ctx, user_id: str):
    return Div(f"User {user_id}")
```

## Path Parameters

MikiUI supports type-coerced path parameters:

```python
@app.route("/users/{user_id:int}")
def get_user(ctx, user_id: int):
    return Div(f"User {user_id}")

@app.route("/posts/{post_id:uuid}")
def get_post(ctx, post_id: uuid.UUID):
    return Div(f"Post {post_id}")

@app.route("/files/{path:path}")
def get_file(ctx, path: str):
    return Div(f"File: {path}")
```

Supported types: `int`, `float`, `uuid`, `path`, `str` (default).

## HTTP Methods

Use the convenience methods for common HTTP verbs:

```python
@app.get("/items")
def list_items():
    return Div("Items")

@app.post("/items")
def create_item():
    return Div("Created")

@app.put("/items/{item_id}")
def update_item(item_id: str):
    return Div("Updated")

@app.patch("/items/{item_id}")
def patch_item(item_id: str):
    return Div("Patched")

@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    return Div("Deleted")
```

## Route Groups

Group routes that share a prefix, auth, and middleware:

```python
from mikiui.router.auth import AuthRequirement
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

## Routers

Organize routes into separate modules using `Router`:

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

# app.py
from mikiui import MikiApp
from routes.users import router as user_router

app = MikiApp()
app.mount(user_router)
```

## Nested Routers

```python
api = Router(prefix="/api")
v1 = Router(prefix="/v1")
api.mount(v1)

@v1.get("/items")
def items():
    return Div("items")  # mounted at /api/v1/items
```

## Custom 404 and Error Pages

```python
@app.not_found
def not_found(ctx):
    return Div("This page does not exist.")

app.set_error_page(403, lambda ctx: Div("Access denied"))
app.set_error_page(500, lambda ctx: Div("Something went wrong"))
```

## See Also

- [Security Guide](../guide/security.md) — auth, CSRF, rate limiting
- [API Reference](../guide/api-reference.md) — full routing API

## Router Details

### Separate Route Files

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

### Two Usage Patterns

#### 1. Explicit (no mount needed)

Pass the app as the first argument to each decorator:

```python
router = Router(prefix="/admin")

@router.get(app, "/dashboard")
def admin_dashboard():
    return Div("Admin Dashboard")
```

#### 2. Mounted (bare decorators)

Mount the router first, then use bare decorators:

```python
router = Router(prefix="/admin")
app.mount(router)

@router.get("/dashboard")
def admin_dashboard():
    return Div("Admin Dashboard")
```

Both patterns produce identical route entries in `app.routes`.

### Nested Routers

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

### Route Name Uniqueness

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
