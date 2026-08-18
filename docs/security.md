# Security Guide

MikiUI ships with production-grade security defaults. This guide covers the
built-in protections and how to use them.

---

## 1. Security Headers

MikiUI adds security headers to every response via
`SecurityHeadersMiddleware`.

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking |
| `Referrer-Policy` | `no-referrer` | Blocks referrer leakage |
| `Cross-Origin-Opener-Policy` | `same-origin` | Prevents cross-origin opener attacks |
| `Cross-Origin-Embedder-Policy` | `require-corp` | Prevents cross-origin embedder attacks |
| `X-Permitted-Cross-Domain-Policies` | `none` | Blocks cross-domain policy files |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Enforces HTTPS (when HTTPS is used) |
| `Permissions-Policy` | Restricts geolocation, mic, camera, payment, usb | Limits browser API access |
| `Content-Security-Policy` | Baseline policy + per-request nonce | Prevents XSS and data injection |

### CSP Nonces

Every response gets a unique CSP nonce injected automatically. Use it when
inlining scripts:

```python
from starlette.requests import Request

@app.route("/")
def home(request: Request):
    nonce = getattr(request.state, "csp_nonce", "")
    return Div(
        Script(f'console.log("hello");', nonce=nonce)
    )
```

---

## 2. CORS (Cross-Origin Resource Sharing)

CORS is configured when creating the FastAPI app:

```python
from mikiui.backend.server import create_app

app = create_app(
    miki_app,
    runtime="local",
    cors_origins=["https://example.com", "https://admin.example.com"],
)
```

### Rules

- **Never** use `cors_origins=["*"]` with `allow_credentials=True` — MikiUI
  blocks this combination automatically.
- Allowed methods are restricted to safe defaults:
  `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`.
- Allowed headers are restricted to:
  `Accept`, `Accept-Language`, `Content-Language`, `Content-Type`,
  `Authorization`, `X-CSRF-Token`.
- Preflight results are cached for 600 seconds (`max_age=600`).

---

## 3. CSRF Protection

MikiUI includes `CSRFMiddleware` that validates tokens on state-changing
requests.

### How it works

- **Safe methods** (`GET`, `HEAD`, `OPTIONS`) bypass validation.
- **Unsafe methods** (`POST`, `PUT`, `PATCH`, `DELETE`) require a valid
  CSRF token.
- Tokens are checked from:
  1. `X-CSRF-Token` header (preferred for AJAX/HTMX)
  2. `_csrf` form field (for HTML forms)
- Tokens are bound to the session and signed with HMAC-SHA256.
- Validation uses timing-safe comparison (`hmac.compare_digest`).

### Usage

```python
from mikiui.router.csrf import CSRFMiddleware
from mikiui.backend.server import create_app

app = create_app(miki_app)

app.add_middleware(
    CSRFMiddleware,
    get_session_token=lambda request: request.cookies.get("mikiui_session"),
    validate_csrf=lambda session_token, csrf_token: miki_app.validate_csrf(session_token, csrf_token),
    exempt_paths=["/webhook/"],
)
```

### Frontend integration

Include the CSRF token in HTMX requests:

```html
<meta name="csrf-token" content="{{ csrf_token }}">
<script>
  document.addEventListener('htmx:configRequest', (event) => {
    const token = document.querySelector('meta[name="csrf-token"]')?.content;
    if (token) {
      event.detail.headers['X-CSRF-Token'] = token;
    }
  });
</script>
```

---

## 4. Cookie Security

MikiUI sets session cookies with secure attributes by default.

### Cookie attributes

| Attribute | Default | Purpose |
|-----------|---------|---------|
| `HttpOnly` | `True` | Prevents JavaScript access (XSS protection) |
| `Secure` | `True` | Only sent over HTTPS |
| `SameSite` | `Lax` | Prevents CSRF via cross-site requests |
| `Max-Age` | Session lifetime | Controls cookie persistence |

### Setting cookies

```python
from fastapi.responses import JSONResponse

@app.route("/login")
def login():
    token = app.create_session("user123")
    response = JSONResponse({"status": "ok"})
    app.set_session_cookie(response, token)
    return response
```

### Deleting cookies

```python
@app.route("/logout")
def logout():
    app.destroy_session(token)
    response = JSONResponse({"status": "ok"})
    app.delete_session_cookie(response)
    return response
```

---

## 5. Session Management

Sessions are signed with HMAC-SHA256 and stored in memory by default.

### Features

- **Token signing** — tokens include a truncated HMAC signature.
- **Timing-safe validation** — `hmac.compare_digest` prevents timing attacks.
- **Expiration** — tokens expire after `session_lifetime` (default: 24 hours).
- **Rotation** — `rotate_session()` invalidates the old token and issues a new one.
- **Per-user limits** — configurable max sessions per user with FIFO eviction.

### Session storage

The default in-memory store is suitable for single-process development.
For production, use a shared backend:

```python
from mikiui_app_plugins.session import SessionPlugin

session = SessionPlugin(
    secret_key="your-secret-key",
    session_lifetime=timedelta(hours=24),
    max_sessions_per_user=5,
    # storage=RedisSessionStorage(redis_url="redis://localhost:6379/0"),
)
```

### Best practices

- **Rotate sessions on login** — call `rotate_session()` after authentication.
- **Set short lifetimes** — 24 hours for normal sessions, shorter for sensitive apps.
- **Use HTTPS** — always set `secure=True` on cookies in production.
- **Store secret keys securely** — use environment variables, never hardcode.

---

## 6. Authentication & Authorization

MikiUI uses a pluggable auth strategy system. Built-in strategies include
`"session"` (from `SessionPlugin`) and `"token"` (bearer tokens). Custom
strategies can be registered via `app.register_auth_strategy(name, strategy)`.

### AuthRequirement

Declare auth requirements declaratively using `AuthRequirement`:

```python
from mikiui.router.auth import AuthRequirement

# Public route
@app.route("/about")
def about():
    return Div("About")

# Require session auth
@app.route("/dashboard", auth=AuthRequirement(strategy="session"))
def dashboard(ctx):
    return Div("Dashboard")

# Require JWT with scopes
@app.route("/admin", auth=AuthRequirement(strategy="jwt", scopes=["admin"]))
def admin(ctx):
    return Div("Admin")
```

### Per-route-group auth

Apply auth to an entire route group:

```python
from mikiui.router.auth import AuthRequirement

api = app.route_group("/api")
api.auth(AuthRequirement(strategy="jwt", scopes=["user"]))

@api.get("/profile")
def profile(ctx):
    return Div("Your profile")
```

### Legacy `requires_auth`

The `requires_auth=True` shorthand still works and defaults to the `"session"`
strategy:

```python
@app.route("/secret", requires_auth=True)
def secret():
    return Div("Secret data")
```

### Auth strategies

A strategy is any callable with a `validate(request) -> user | None` method.
Register custom strategies:

```python
def validate_jwt(request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    return decode_jwt(token)

app.register_auth_strategy("jwt", validate_jwt)
```

### Session strategy

When `SessionPlugin` is active, MikiUI auto-registers a `"session"` strategy
that reads the `mikiui_session` cookie or `Authorization` header.

### API authentication

```python
from mikiui_app_plugins.api import APIPlugin

api = APIPlugin(session_plugin=session)
app.use(api)
```

Clients send the session token via:
- Cookie: `mikiui_session=<token>`
- Header: `Authorization: Bearer <token>`

---

## 7. Rate Limiting

`RateLimitMiddleware` provides in-memory sliding-window rate limiting.

### Defaults

| Scope | Limit | Window |
|-------|-------|--------|
| General endpoints | 100 requests | 60 seconds |
| Auth endpoints (`/login`, `/auth`, `/api/auth`) | 10 requests | 60 seconds |

### Usage

```python
from mikiui.router.rate_limit import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    general_limit=100,
    general_window=60,
    auth_limit=10,
    auth_window=60,
)
```

When a client exceeds the limit, the middleware returns:
- Status: `429 Too Many Requests`
- Header: `Retry-After: <seconds>`
- Body: `{"error": "Too many requests", "retry_after": <seconds>}`

---

## 8. WebSocket Security

WebSocket connections are validated before acceptance.

### Security checks

1. **Origin validation** — rejects connections from untrusted origins.
2. **Optional auth** — validates a session token from query params or headers.
3. **Connection limits** — max connections per user and per IP.
4. **Message size limits** — default 1MB per message.

### Usage

```python
from mikiui.backend.websocket import ConnectionManager, mount_websocket

manager = ConnectionManager(
    max_connections_per_user=5,
    max_connections_per_ip=10,
    max_message_size=1024 * 1024,  # 1MB
    allowed_origins=["https://example.com"],
    validate_token=lambda token: app.validate_session(token) and token.user_id,
)

mount_websocket(router, "/ws", handler, manager=manager)
```

---

## 9. Input Validation & XSS Prevention

MikiUI escapes all HTML content by default:

- **Text content** — escaped with `html.escape()`
- **Attributes** — escaped before rendering
- **URLs** — validated before use

### Alpine.js safety

When binding user data in Alpine.js, use the `x-text` directive (auto-escaped)
instead of `x-html` (raw HTML):

```html
<!-- Safe: auto-escaped -->
<div x-text="userInput"></div>

<!-- Dangerous: raw HTML, only use for trusted content -->
<div x-html="trustedHtml"></div>
```

---

## 10. Security Checklist

Use this checklist when deploying a MikiUI app:

- [ ] **HTTPS** — always use HTTPS in production.
- [ ] **Secret keys** — use strong, randomly generated keys stored in env vars.
- [ ] **CORS origins** — restrict to your actual domains, never `["*"]` with credentials.
- [ ] **Cookie security** — ensure `HttpOnly`, `Secure`, `SameSite` are set.
- [ ] **Session lifetime** — set appropriate expiration times.
- [ ] **Rate limiting** — enable for production, tighten auth endpoint limits.
- [ ] **WebSocket origins** — restrict to your domains.
- [ ] **Input validation** — validate all user input server-side.
- [ ] **Dependencies** — keep FastAPI, uvicorn, and other deps up to date.
- [ ] **Error handling** — don't expose stack traces or internal details in production.

---

## 11. Reporting Security Issues

If you find a security vulnerability, please report it privately to
[security@mikiui.dev](mailto:security@mikiui.dev) instead of opening a public issue.
