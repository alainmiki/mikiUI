# MikiUI Routing System — Scalability Overhaul Plan

## Goal

Fix every bug and hardcoded assumption in the current routing/middleware/auth/build stack so MikiUI can serve large applications (hundreds of routes, multiple route groups, mixed auth zones, incremental builds) without breaking changes to the beginner-friendly API.

---

## 1. Fix Router Prefix Concatenation

**Problem:** `Router.mount` concatenates prefixes without a separator (`"/api" + "/v1" = "/apiv1"`).

**Change:** In `mikiui/router/router.py`, `Router.mount` must join prefixes with `/` using `posixpath.join` or equivalent.

```python
import posixpath

def mount(self, target: MikiApp | Router) -> Router:
    if isinstance(target, Router):
        combined = posixpath.join(self.prefix or "", target.prefix or "")
        target.prefix = combined.rstrip("/") or combined
        target._parent = self
    else:
        self._app = target
    return self
```

**Test:** `test_nested_routers` in `tests/test_router.py` must pass.

---

## 2. Route Name Uniqueness Validation

**Problem:** Two handlers named `home()` on different paths collide in `url_for`. The duplicate path check in `MikiApp.route` does not catch name collisions.

**Change:** Add `_validate_route_name` in `mikiui/app/app.py`:

```python
def _validate_route_name(self, name: str | None, handler: Callable) -> None:
    name = name or getattr(handler, "__name__", "route")
    existing = next((r for r in self.routes.values() if r.name == name), None)
    if existing is not None:
        raise ValueError(
            f"Route name {name!r} is already used by {existing.path!r}. "
            "Pass a unique `name=` to the decorator."
        )
```

Call it in the `route` decorator before storing.

---

## 3. 404 / Not-Found Handler

**Problem:** FastAPI's default 404 returns JSON. There is no catch-all route or branded error page.

**Change:**

1. Add `MikiApp.not_found(handler)` decorator that stores a single `not_found_handler` on the app.
2. In `backend/server.py::create_app`, after registering all app routes, register a `app.add_api_route("/{full_path:path}", _not_found_endpoint, include_in_schema=False)` that:
   - Invokes `miki_app.not_found_handler` if set,
   - Otherwise returns `error_response(NotFoundError("page"), request)`.
3. Ensure `RouteDef.accepts_ctx` is respected so the handler can inspect the request.

**API:**

```python
@app.not_found
def not_found(ctx):
    return Div("Page not found")
```

**Test:** 404 on unknown path returns 200 if custom handler is set, 404 with HTML body otherwise.

---

## 4. Client-Side History Router (SPA Mode)

**Problem:** No `history.pushState` router. Static builds and separate-mode deployments cannot navigate without full reloads.

**Change:**

1. Add `mikiui/router/history_router.py` — a lightweight JS router that:
   - Listens for `click` on `<a>` with same-origin `href`,
   - Calls `history.pushState`,
   - Fires `miki:navigate` with `{path, method}`.
   - Listens for `popstate` to back/forward navigate.
   - Exposes `window.mikiRouter`.
2. Add `Router.add_history_routes(app)` that decorates the FastAPI app with an endpoint returning the current page's fragment (for JS fetch) — optional, since the main FastAPI routes still work.
3. Update `runtime_loader.py` to include `history_router.js` in the default script bundle.
4. Add a `runtime="spa"` mode that loads the history router.
5. Update `BASE_TEMPLATE` in `engine/renderer.py` to emit a `<nav data-miki-nav>` shell that the JS router can auto-bind.

**Constraint:** The history router must be opt-in so beginners still get plain MPAs.

---

## 5. Pluggable Per-Route-Group Auth

**Problem:** `requires_auth` is a boolean. The `SessionPlugin` cookie name is hardcoded to `mikiui_session`. There is no way to say "this group needs JWT, that group needs session, this group is public."

**Change:**

1. Introduce `AuthRequirement` dataclass in `mikiui/router/auth.py`:

```python
@datac_field
class AuthRequirement:
    strategy: str  # "session" | "jwt" | "token" | "none"
    cookie_name: str | None = None
    header_name: str | None = None
    query_param: str | None = None
    scopes: list[str] = field(default_factory=list)
    redirect_to: str | None = "/login"
```

2. Change `RouteDef.requires_auth` from `bool` to `AuthRequirement | None`.
3. Change `MikiApp.route` decorator to accept `auth: AuthRequirement | bool | None = None`.
4. Remove the hardcoded `request.cookies.get("mikiui_session")` check from `backend/server.py`. Replace it with a pluggable `AuthMiddleware` that:
   - Reads `app.auth_strategies: dict[str, Callable]`,
   - Resolves the strategy per route,
   - Calls the appropriate validator.
5. Add `AuthStrategy` protocol in `mikiui/router/auth.py` with `validate(request) -> user | None`.
6. `SessionPlugin` registers its strategy under `"session"`. `APIPlugin` (or a new `JWTPlugin`) registers under `"jwt"`.
7. `Router` accepts `auth: AuthRequirement` in `__init__` and applies it to all child routes unless overridden.

**Backward compat:** `requires_auth=True` still works by converting to `AuthRequirement(strategy="session")`.

---

## 6. Pluggable Per-Route-Group Middleware

**Problem:** `apply_default_middleware` is global. `RateLimitMiddleware` and `CSRFMiddleware` cannot be scoped to a route group.

**Change:**

1. Add `RouteGroup` class in `mikiui/router/group.py`:

```python
class RouteGroup:
    prefix: str
    auth: AuthRequirement | None
    middleware: list[type]
    rate_limit: RateLimitConfig | None
    csrf: CSRFConfig | None
    routes: list[RouteDef]
```

2. `MikiApp.route_group(prefix)` returns a `RouteGroupBuilder` that supports:
   - `group.auth(AuthRequirement(...))`
   - `group.use(middleware_class)`
   - `group.rate_limit(limit=100, window=60)`
   - `group.csrf(exempt_paths=[...])`
3. `Router` becomes a thin wrapper around `RouteGroup`. Nested routers inherit and merge group configs.
4. `backend/server.py::create_app` iterates route groups, mounts per-group middleware stacks before the endpoint.
5. `RateLimitMiddleware` accepts a `key_func: Callable[[Request], str]` so keys can be `user_id` (when authenticated) or `ip` as fallback, instead of always `ip:path`.
6. `CSRFMiddleware` accepts `exempt_paths` and `exempt_methods` per group.
7. `SecurityHeadersMiddleware` accepts per-group CSP overrides.

**API example:**

```python
api = app.route_group("/api")
api.rate_limit(limit=200, window=60)
api.auth(AuthRequirement(strategy="jwt", scopes=["admin"]))

@api.get("/admin/users")
def list_users(ctx):
    return Div("users")
```

---

## 7. Rate Limiter TTL / Eviction

**Problem:** `_SlidingWindowLimiter` stores unbounded `list[float]` per `ip:path` key. Memory grows forever.

**Change:** Add a `max_keys` cap and periodic cleanup in `mikiui/router/rate_limit.py`:

1. Add `max_keys: int = 100_000` to `RateLimitMiddleware.__init__`.
2. When `_hits` exceeds `max_keys`, evict the oldest 20% of keys (FIFO by first-access timestamp).
3. Add a per-key TTL (`key_ttl: int = 3600`) — keys not hit within `key_ttl` seconds are removed.
4. Expose `RateLimitMiddleware.stats()` returning `{"active_keys": ..., "evicted": ...}` for observability.

---

## 8. Build System for Large Apps

**Problem:** `build_web` renders every GET route synchronously. No incremental build, no caching, no parallelization.

**Change:**

1. Add `mikiui/build/incremental.py`:
   - Compute a manifest of `route_path -> hash(handler_source, theme, dependencies)`.
   - Skip rendering if hash matches previous build.
   - Render only changed routes.
2. Parallelize route rendering with `asyncio.Semaphore(concurrency)` and `asyncio.gather` in `_export_route`.
3. Add `build_web(..., concurrency: int = 4)` parameter.
4. Generate `sitemap.xml` in `build_web` for all rendered routes.
5. Add `prerender=True` flag that injects JSON-LD and meta tags for crawlers.
6. For parameterized routes in static export:
   - If a route has `{param}` placeholders, render a "shell" HTML file plus a `route-manifest.json` mapping example paths.
   - Document that fully static export of dynamic routes requires the fullstack server or an adapter (e.g., Cloudflare Workers).
   - Raise a clear `UserWarning` during build for parameterized routes, rather than silently skipping.

---

## 9. CSP Nonce Per-Request Safety

**Problem:** `SecurityHeadersMiddleware` stores `self._nonce` as an instance attribute. Concurrent requests overwrite each other.

**Change:** Move nonce storage to `request.state`:

```python
async def dispatch(self, request: Request, call_next):
    nonce = secrets.token_urlsafe(16)
    request.state.csp_nonce = nonce
    response = await call_next(request)
    ...
    if nonce:
        response.headers.setdefault("Content-Security-Policy", f"{csp} 'nonce-{nonce}'")
    return response
```

Remove `self._nonce` entirely.

---

## 10. Router.mount Immutability

**Problem:** `Router.mount` mutates `target.prefix` in place. Re-using the same router instance across tests/apps corrupts state.

**Change:** Make `Router.prefix` a computed property backed by `_prefix`:

```python
class Router:
    def __init__(self, prefix: str = ""):
        self._prefix = prefix.rstrip("/")
        self._app: MikiApp | None = None
        self._parent: Router | None = None

    @property
    def prefix(self) -> str:
        parts = []
        node: Router | None = self
        while node is not None:
            if node._prefix:
                parts.append(node._prefix)
            node = node._parent
        return "/" + "/".join(reversed(parts)) if parts else ""

    @prefix.setter
    def prefix(self, value: str) -> None:
        self._prefix = value.rstrip("/")
```

`mount` no longer mutates the child's prefix directly; it sets `_parent`.

---

## 11. Static Asset Mount Safety

**Problem:** `static_assets.py::discover` clears `_ASSET_MOUNTS` and `_ABS_TO_URL` on every call, which is fine, but `register_plugin_assets` mutates the same dicts concurrently if called during discovery.

**Change:** Make `register_plugin_assets` idempotent and atomic. Add a `register_package_root` call for `mikiui_app_plugins` in `init_defaults` so plugin assets are auto-discovered without explicit registration.

---

## 12. Error Page Customization

**Problem:** `_render_error_html` in `mikiui/errors.py` returns a hardcoded `<div>`.

**Change:**

1. Add `MikiApp.set_error_page(status_code, handler)` that stores handlers in `self._error_pages: dict[int, Callable]`.
2. `error_response` checks `app._error_pages` before falling back to the default HTML.
3. Allow a single `@app.not_found` handler (see item 3) that doubles as the 404 page.

---

## Implementation Order

| Phase | Items | Description |
|-------|-------|-------------|
| **1 — Core correctness** | 1, 2, 9, 10 | Fix the prefix bug, name collisions, nonce race, and mount mutation. These are blockers. |
| **2 — Auth overhaul** | 5 | Pluggable per-route-group auth. Depends on RouteGroup (phase 3) but the strategy registry can be built independently. |
| **3 — Route groups** | 6 | Pluggable per-group middleware, rate limiting, CSRF. Depends on phase 1. |
| **4 — Error UX** | 3, 12 | 404 handler and customizable error pages. |
| **5 — Build scalability** | 8 | Incremental/parallel static export. Independent of phases 1-4. |
| **6 — SPA mode** | 4 | Client-side history router. Can ship after phases 1-3. |
| **7 — Polish** | 7, 11 | Rate limiter eviction + static asset safety. |

---

## Test Plan

- `tests/test_router.py` — add cases for nested prefix, duplicate name rejection, not-found handler, route-group middleware.
- `tests/test_middleware.py` — new file: per-group auth, per-group rate limit, CSP nonce concurrency test (2 simultaneous requests assert distinct nonces).
- `tests/test_build.py` — add incremental build test, parameterized-route warning test, sitemap generation test.
- `tests/test_spa.py` — new file: history router navigation test (if JS runtime is testable with Playwright).

All new tests must pass under `pytest tests/ -q`.

---

## Non-Goals (Out of Scope)

- Actual JWT implementation (only the strategy hook is added; a `JWTPlugin` would be a separate plugin).
- Distributed rate limiting (Redis-backed limiter is a plugin concern).
- Multi-tenant routing (tenant prefix extraction is app-specific).
- Desktop-specific routing differences (already handled by `build/desktop_build.py`).

---

## Migration Path

1. `requires_auth=True` continues to work (auto-converts to `AuthRequirement(strategy="session")`).
2. `RouteDef.name` auto-generation unchanged; only duplicates now raise.
3. `build_web` signature gains optional kwargs (`concurrency`, `skip_existing`); defaults preserve current behavior.
4. `SecurityHeadersMiddleware` signature unchanged; `request.state.csp_nonce` is additive.
5. `Router.mount` behavior unchanged for callers; only the internal prefix storage is immutable.

No breaking changes to existing user code.
