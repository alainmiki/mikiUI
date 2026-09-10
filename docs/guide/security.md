# Security

MikiUI ships with production-grade security defaults. This guide covers the built-in protections and how to use them.

## Security Headers

MikiUI adds security headers to every response:

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME-type sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking |
| `Referrer-Policy` | `no-referrer` | Blocks referrer leakage |
| `Cross-Origin-Opener-Policy` | `same-origin` | Prevents cross-origin opener attacks |
| `Cross-Origin-Embedder-Policy` | `require-corp` | Prevents cross-origin embedder attacks |
| `X-Permitted-Cross-Domain-Policies` | `none` | Blocks cross-domain policy files |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Enforces HTTPS |
| `Permissions-Policy` | Restricts geolocation, mic, camera, payment, usb | Limits browser API access |
| `Content-Security-Policy` | Baseline policy + per-request nonce | Prevents XSS and data injection |

## CSP Nonces

Every response gets a unique CSP nonce injected automatically. Use it when inlining scripts:

```python
from starlette.requests import Request

@app.route("/")
def home(request: Request):
    nonce = getattr(request.state, "csp_nonce", "")
    return Div(
        Script(f'console.log("hello");', nonce=nonce)
    )
```

## CORS

CORS is configured when creating the FastAPI app:

```python
from mikiui.backend.server import create_app

app = create_app(
    miki_app,
    runtime="local",
    cors_origins=["https://example.com", "https://admin.example.com"],
)
```

**Never** use `cors_origins=["*"]` with `allow_credentials=True` — MikiUI blocks this automatically.

## CSRF Protection

CSRF protection is **enabled by default**. MikiUI includes `CSRFMiddleware` that validates tokens on state-changing requests using the double-submit cookie pattern.

### How it works

- **Safe methods** (`GET`, `HEAD`, `OPTIONS`) bypass validation.
- **Unsafe methods** (`POST`, `PUT`, `PATCH`, `DELETE`) require a valid CSRF token.
- The server sets a `mikiui_csrf` cookie on responses.
- The client echoes the cookie value in the `X-CSRF-Token` header or `_csrf` form field.

### Frontend integration

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

## Cookie Security

MikiUI sets session cookies with secure attributes by default:

| Attribute | Default | Purpose |
|-----------|---------|---------|
| `HttpOnly` | `True` | Prevents JavaScript access (XSS protection) |
| `Secure` | `True` | Only sent over HTTPS |
| `SameSite` | `Lax` | Prevents CSRF via cross-site requests |

## Session Management

Sessions are signed with HMAC-SHA256 and stored in memory by default. For production, use a shared backend:

```python
from mikiui_app_plugins.session import SessionPlugin

session = SessionPlugin(
    secret_key="your-secret-key",
    session_lifetime=timedelta(hours=24),
    max_sessions_per_user=5,
    # storage=RedisSessionStorage(redis_url="redis://localhost:6379/0"),
)
```

## Authentication & Authorization

MikiUI uses a pluggable auth strategy system:

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

## Rate Limiting

`RateLimitMiddleware` provides in-memory sliding-window rate limiting:

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

## Input Validation & XSS Prevention

MikiUI escapes all HTML content by default:

- **Text content** — escaped with `html.escape()`
- **Attributes** — escaped before rendering
- **URLs** — validated before use

When binding user data in Alpine.js, use `x-text` (auto-escaped) instead of `x-html` (raw HTML):

```html
<!-- Safe: auto-escaped -->
<div x-text="userInput"></div>

<!-- Dangerous: raw HTML, only use for trusted content -->
<div x-html="trustedHtml"></div>
```

## Plugin Security

MikiUI validates every plugin before loading. The framework enforces a configurable security policy:

```python
from mikiui.app import PluginSecurityConfig

config = PluginSecurityConfig(
    allow_untrusted=False,
    vet_ast=True,
    blocked_capabilities=["filesystem:write"],
)
app.set_plugin_security_config(config)
```

### What gets checked

1. **Identity check** — plugin name matches its manifest
2. **Capability check** — declared capabilities are not in the blocked list
3. **AST vetting** — source code is scanned for dangerous patterns
4. **Import scanning** — only allow-listed top-level modules may be imported

Plugins that fail validation raise `PluginSecurityViolation` and are **not registered**.

## Security Checklist

- [ ] **HTTPS** — always use HTTPS in production
- [ ] **Secret keys** — use strong, randomly generated keys stored in env vars
- [ ] **CORS origins** — restrict to your actual domains
- [ ] **Cookie security** — ensure `HttpOnly`, `Secure`, `SameSite` are set
- [ ] **Session lifetime** — set appropriate expiration times
- [ ] **Rate limiting** — enable for production
- [ ] **WebSocket origins** — restrict to your domains
- [ ] **Input validation** — validate all user input server-side
- [ ] **Dependencies** — keep FastAPI, uvicorn, and other deps up to date

## Reporting Security Issues

If you find a security vulnerability, please report it privately to [security@mikiui.dev](mailto:security@mikiui.dev) instead of opening a public issue.
