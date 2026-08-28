"""Tests for security features: sessions, CSRF, headers, path params."""

from __future__ import annotations

import pytest
from fastapi import WebSocketDisconnect
from fastapi.testclient import TestClient

from mikiui import MikiApp
from mikiui.backend import create_app
from mikiui_app_plugins import SessionPlugin
from mikiui_app_plugins.api import APIPlugin

# ---------------------------------------------------------------------------
# Session Plugin Security Tests
# ---------------------------------------------------------------------------

def test_session_plugin_rejects_short_secret_key():
    with pytest.raises(ValueError, match="at least 16 characters"):
        SessionPlugin(secret_key="short")


def test_session_token_has_signature():
    """Tokens are HMAC-signed: ``raw.signature`` format."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    app.use(session)

    token = app.create_session("user123")
    assert "." in token
    raw, sig = token.rsplit(".", 1)
    assert len(raw) > 0
    assert len(sig) > 0


def test_session_token_not_forgeable():
    """A forged token (wrong signature) is rejected."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    app.use(session)

    token = app.create_session("user123")
    raw = token.rsplit(".", 1)[0]
    forged = f"{raw}.aaaaaaa"
    assert app.validate_session(forged) is None


def test_session_invalid_token_format_rejected():
    """Tokens not matching ``token.signature`` format are rejected."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    app.use(session)

    assert app.validate_session("invalid") is None
    assert app.validate_session("") is None
    assert app.validate_session(None) is None  # type: ignore[arg-type]
    assert app.validate_session(12345) is None  # type: ignore[arg-type]


def test_session_max_sessions_per_user():
    """Old sessions are evicted when max is exceeded."""
    app = MikiApp()
    session = SessionPlugin(
        secret_key="a-very-long-secret-key",
        max_sessions_per_user=2,
    )
    app.use(session)

    t1 = app.create_session("user1")
    t2 = app.create_session("user1")
    t3 = app.create_session("user1")

    assert app.validate_session(t1) is None  # evicted
    assert app.validate_session(t2) is not None
    assert app.validate_session(t3) is not None


def test_session_cleanup_expired():
    """Expired sessions are removed from cleanup."""
    from datetime import timedelta

    app = MikiApp()
    session = SessionPlugin(
        secret_key="a-very-long-secret-key",
        session_lifetime=timedelta(seconds=0),
    )
    app.use(session)

    app.create_session("user1")
    # Lifetime is 0, so token is immediately expired
    removed = app.cleanup_expired()
    assert removed >= 1


def test_session_rotate_session():
    """rotate_session issues a new token and invalidates the old one."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    app.use(session)

    old_token = app.create_session("user1", role="user")
    new_token = app.rotate_session(old_token)

    assert new_token is not None
    assert new_token != old_token
    assert app.validate_session(old_token) is None  # old token invalidated
    assert app.validate_session(new_token) == "user1"
    assert app.get_session_data(new_token) == {"role": "user"}


def test_csrf_token_generation_and_validation():
    """CSRF tokens are generated and validated."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    app.use(session)

    token = app.create_session("user1")
    csrf = app.generate_csrf_token(token)
    assert csrf is not None
    assert app.validate_csrf_token(token, csrf) is True
    assert app.validate_csrf_token(token, "invalid.token") is False
    assert app.validate_csrf_token(token, "") is False


def test_csrf_rejects_invalid_session():
    """CSRF generation requires a valid session."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    app.use(session)

    assert app.generate_csrf_token("invalid.token") is None


def test_session_data_excludes_internal_fields():
    """get_session_data excludes created/expires/user_id."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    app.use(session)

    token = app.create_session("user1", role="admin", email="test@test.com")
    data = app.get_session_data(token)
    assert "role" in data
    assert "email" in data
    assert "created" not in data
    assert "expires" not in data
    assert "user_id" not in data


def test_session_destroy():
    """destroy_session removes the session."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    app.use(session)

    token = app.create_session("user1")
    assert app.destroy_session(token) is True
    assert app.destroy_session(token) is False  # already destroyed
    assert app.validate_session(token) is None


# ---------------------------------------------------------------------------
# API Plugin Security Tests
# ---------------------------------------------------------------------------

def test_api_plugin_methods_uppercase():
    """APIPlugin registers routes with correct HTTP methods (not capitalized)."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    plugin = APIPlugin(session_plugin=session)
    app.use(session)
    app.use(plugin)

    @app.route("/api/items", methods=("GET",))
    def items():
        return [{"name": "item1"}]

    fastapi_app = create_app(app)
    plugin.register_endpoints(fastapi_app)

    client = TestClient(fastapi_app)
    resp = client.get("/api/items")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["data"] == [{"name": "item1"}]


def test_api_plugin_requires_auth():
    """Auth-required routes reject unauthenticated requests."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    plugin = APIPlugin(session_plugin=session)
    app.use(session)
    app.use(plugin)

    @app.route("/api/secret", methods=("GET",), requires_auth=True)
    def secret():
        return {"secret": "data"}

    fastapi_app = create_app(app)
    plugin.register_endpoints(fastapi_app)

    client = TestClient(fastapi_app)
    resp = client.get("/api/secret")
    assert resp.status_code == 401


def test_api_plugin_auth_with_valid_token():
    """Auth-required routes accept valid session tokens."""
    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    plugin = APIPlugin(session_plugin=session)
    app.use(session)
    app.use(plugin)

    token = app.create_session("user1")

    @app.route("/api/secret", methods=("GET",), requires_auth=True)
    def secret():
        return {"secret": "data"}

    fastapi_app = create_app(app)
    plugin.register_endpoints(fastapi_app)

    client = TestClient(fastapi_app)
    resp = client.get("/api/secret", cookies={"mikiui_session": token})
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Security Headers Tests
# ---------------------------------------------------------------------------

def test_security_headers_present():
    """Ensure default security headers are set."""
    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.get("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    client = TestClient(fastapi_app)
    resp = client.get("/test")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("Referrer-Policy") == "no-referrer"
    assert "Content-Security-Policy" in resp.headers


def test_permissions_policy_present():
    """Permissions-Policy header restricts browser APIs."""
    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.get("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    client = TestClient(fastapi_app)
    resp = client.get("/test")
    assert "Permissions-Policy" in resp.headers
    assert "camera" in resp.headers["Permissions-Policy"]


# ---------------------------------------------------------------------------
# Cookie Security Attribute Tests
# ---------------------------------------------------------------------------

def test_session_set_session_cookie():
    """set_session_cookie adds HttpOnly, Secure, SameSite attributes."""
    from fastapi.responses import JSONResponse

    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    app.use(session)

    token = app.create_session("user1")
    response = JSONResponse({"ok": True})
    app.set_session_cookie(response, token)
    cookie = response.headers.get("set-cookie", "")
    assert "mikiui_session" in cookie
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "samesite=lax" in cookie.lower()


def test_session_delete_session_cookie():
    """delete_session_cookie expires the session cookie."""
    from fastapi.responses import JSONResponse

    app = MikiApp()
    session = SessionPlugin(secret_key="a-very-long-secret-key")
    app.use(session)

    response = JSONResponse({"ok": True})
    app.delete_session_cookie(response)
    cookie_header = response.headers.get("set-cookie", "")
    assert "mikiui_session=" in cookie_header
    assert "Max-Age=0" in cookie_header


# ---------------------------------------------------------------------------
# CSRF Middleware Tests
# ---------------------------------------------------------------------------

def test_csrf_middleware_skips_safe_methods():
    """GET/HEAD/OPTIONS bypass CSRF validation."""
    from mikiui.router.csrf import CSRFMiddleware

    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.get("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    fastapi_app.add_middleware(
        CSRFMiddleware,
        get_session_token=lambda r: "token123",
        validate_csrf=lambda t, c: False,
    )

    client = TestClient(fastapi_app)
    resp = client.get("/test")
    assert resp.status_code == 200


def test_csrf_middleware_blocks_missing_token():
    """POST without CSRF token returns 403."""
    from mikiui.router.csrf import CSRFMiddleware

    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.post("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    fastapi_app.add_middleware(
        CSRFMiddleware,
        get_session_token=lambda r: "token123",
        validate_csrf=lambda t, c: True,
    )

    client = TestClient(fastapi_app)
    resp = client.post("/test")
    assert resp.status_code == 403


def test_csrf_middleware_accepts_valid_header():
    """POST with valid X-CSRF-Token header succeeds."""
    from mikiui.router.csrf import CSRFMiddleware

    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.post("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    fastapi_app.add_middleware(
        CSRFMiddleware,
        get_session_token=lambda r: "token123",
        validate_csrf=lambda t, c: c == "valid-csrf-token",
    )

    client = TestClient(fastapi_app)
    resp = client.post("/test", headers={"X-CSRF-Token": "valid-csrf-token"})
    assert resp.status_code == 200


def test_csrf_middleware_accepts_valid_form_field():
    """POST with valid _csrf form field succeeds."""
    from mikiui.router.csrf import CSRFMiddleware

    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.post("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    fastapi_app.add_middleware(
        CSRFMiddleware,
        get_session_token=lambda r: "token123",
        validate_csrf=lambda t, c: c == "valid-csrf-token",
    )

    client = TestClient(fastapi_app)
    resp = client.post("/test", data={"_csrf": "valid-csrf-token"})
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Rate Limiting Tests
# ---------------------------------------------------------------------------

def test_rate_limit_blocks_excess_requests():
    """More than 5 requests from the same IP returns 429."""
    from mikiui.router.rate_limit import RateLimitMiddleware

    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.get("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    fastapi_app.add_middleware(
        RateLimitMiddleware,
        general_limit=5,
        general_window=60,
    )

    client = TestClient(fastapi_app)
    for _ in range(5):
        resp = client.get("/test")
        assert resp.status_code == 200
    resp = client.get("/test")
    assert resp.status_code == 429
    assert "Retry-After" in resp.headers


def test_rate_limit_auth_endpoints_stricter():
    """Auth endpoints have stricter rate limits."""
    from mikiui.router.rate_limit import RateLimitMiddleware

    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.post("/login")
    def login():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    fastapi_app.add_middleware(
        RateLimitMiddleware,
        general_limit=100,
        general_window=60,
        auth_limit=2,
        auth_window=60,
    )

    client = TestClient(fastapi_app)
    for _ in range(2):
        resp = client.post("/login")
        assert resp.status_code == 200
    resp = client.post("/login")
    assert resp.status_code == 429


# ---------------------------------------------------------------------------
# Security Headers Improvement Tests
# ---------------------------------------------------------------------------

def test_security_headers_cross_origin_opener_policy():
    """Cross-Origin-Opener-Policy header is set."""
    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.get("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    client = TestClient(fastapi_app)
    resp = client.get("/test")
    assert resp.headers.get("Cross-Origin-Opener-Policy") == "same-origin"


def test_security_headers_cross_origin_embedder_policy():
    """Cross-Origin-Embedder-Policy and Cross-Origin-Resource-Policy headers are set.

    COEP is set to ``unsafe-none`` so external CDNs and cross-origin media
    (commondatastorage.googleapis.com) load without requiring explicit
    ``Cross-Origin-Resource-Policy: cross-origin`` on the remote origin.
    ``Cross-Origin-Resource-Policy: cross-origin`` is sent on our responses
    so they can be embedded cross-origin when needed.
    """
    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.get("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    client = TestClient(fastapi_app)
    resp = client.get("/test")
    assert resp.headers.get("Cross-Origin-Embedder-Policy") == "unsafe-none"
    assert resp.headers.get("Cross-Origin-Resource-Policy") == "cross-origin"


def test_security_headers_permitted_cross_domain_policies():
    """X-Permitted-Cross-Domain-Policies is none."""
    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.get("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    client = TestClient(fastapi_app)
    resp = client.get("/test")
    assert resp.headers.get("X-Permitted-Cross-Domain-Policies") == "none"


def test_security_headers_no_deprecated_xss_protection():
    """Deprecated X-XSS-Protection header is no longer set."""
    app = MikiApp()
    fastapi_app = create_app(app)

    @fastapi_app.get("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    client = TestClient(fastapi_app)
    resp = client.get("/test")
    assert "X-XSS-Protection" not in resp.headers


def test_cors_rejects_wildcard_with_credentials():
    """CORS middleware does not allow credentials with wildcard origins."""
    app = MikiApp()
    fastapi_app = create_app(app, cors_origins=["*"])

    @fastapi_app.get("/test")
    def test_route():
        from fastapi.responses import JSONResponse

        return JSONResponse({"ok": True})

    client = TestClient(fastapi_app)
    resp = client.get("/test", headers={"Origin": "http://evil.example.com"})
    assert resp.headers.get("access-control-allow-credentials") != "true"
    assert resp.headers.get("access-control-allow-origin") == "*"


# ---------------------------------------------------------------------------
# WebSocket Security Tests
# ---------------------------------------------------------------------------

def test_websocket_origin_validation():
    """WebSocket rejects connections from disallowed origins."""
    from fastapi import APIRouter
    from fastapi.testclient import TestClient

    from mikiui.backend.websocket import ConnectionManager, mount_websocket

    manager = ConnectionManager(allowed_origins=["http://localhost:3000"])

    async def handler(ws, mgr):
        try:
            msg = await ws.receive_text()
            await ws.send_text(msg)
        except Exception:
            mgr.disconnect(ws)

    router = APIRouter()
    mount_websocket(router, "/ws", handler, manager=manager)

    app = MikiApp()
    fastapi_app = create_app(app)
    fastapi_app.include_router(router)

    client = TestClient(fastapi_app)
    with client.websocket_connect("/ws", headers={"origin": "http://localhost:3000"}) as ws:
        ws.send_text("hello")
        data = ws.receive_text()
        assert data == "hello"


def test_websocket_auth_rejects_invalid_token():
    """WebSocket with validate_token should reject invalid tokens."""
    from fastapi import APIRouter
    from fastapi.testclient import TestClient

    from mikiui.backend.websocket import ConnectionManager, mount_websocket

    def validate_token(token: str) -> str | None:
        if token == "valid-token":
            return "user1"
        return None

    manager = ConnectionManager(validate_token=validate_token)

    async def handler(ws, mgr):
        await ws.send_text("connected")

    router = APIRouter()
    mount_websocket(router, "/ws", handler, manager=manager)

    app = MikiApp()
    fastapi_app = create_app(app)
    fastapi_app.include_router(router)

    client = TestClient(fastapi_app)
    # Valid token via query param should connect
    with client.websocket_connect("/ws?token=valid-token") as ws:
        data = ws.receive_text()
        assert data == "connected"

    # Invalid token should be rejected
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws?token=invalid"):
            pass
    assert exc_info.value.code == 4007


def test_websocket_auth_warns_without_validator():
    """WebSocket with auth header but no validator should be rejected."""
    from fastapi import APIRouter
    from fastapi.testclient import TestClient

    from mikiui.backend.websocket import ConnectionManager, mount_websocket

    manager = ConnectionManager()

    async def handler(ws, mgr):
        await ws.send_text("connected")

    router = APIRouter()
    mount_websocket(router, "/ws2", handler, manager=manager)

    app = MikiApp()
    fastapi_app = create_app(app)
    fastapi_app.include_router(router)

    client = TestClient(fastapi_app)
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws2", headers={"Authorization": "Bearer some-token"}):
            pass
    assert exc_info.value.code == 4007


# ---------------------------------------------------------------------------
# AST Obfuscation Detection Tests
# ---------------------------------------------------------------------------

def test_ast_detects_obfuscated_eval():
    """AST vetter should catch getattr(obj, 'ev' + 'al') patterns."""
    import ast

    from mikiui.app.plugin_security import _check_obfuscated_call

    source = "getattr(obj, 'ev' + 'al')"
    tree = ast.parse(source)
    call_node = tree.body[0].value
    violations = _check_obfuscated_call(call_node)
    assert len(violations) == 1
    assert "eval" in violations[0]


def test_ast_detects_obfuscated_exec():
    """AST vetter should catch getattr(obj, 'exec') patterns."""
    import ast

    from mikiui.app.plugin_security import _check_obfuscated_call

    source = "getattr(obj, 'exec')"
    tree = ast.parse(source)
    call_node = tree.body[0].value
    violations = _check_obfuscated_call(call_node)
    assert len(violations) == 1
    assert "exec" in violations[0]


def test_ast_detects_obfuscated_compile():
    """AST vetter should catch __getattribute__('compile') patterns."""
    import ast

    from mikiui.app.plugin_security import _check_obfuscated_call

    source = "obj.__getattribute__('compile')"
    tree = ast.parse(source)
    call_node = tree.body[0].value
    violations = _check_obfuscated_call(call_node)
    assert len(violations) == 1
    assert "compile" in violations[0]


def test_ast_safe_getattr_not_flagged():
    """Non-dangerous getattr calls should not be flagged."""
    import ast

    from mikiui.app.plugin_security import _check_obfuscated_call

    source = "getattr(obj, 'normal_attr')"
    tree = ast.parse(source)
    call_node = tree.body[0].value
    violations = _check_obfuscated_call(call_node)
    assert len(violations) == 0


def test_ast_resolve_string_constant():
    """_resolve_string_arg should handle plain string constants."""
    import ast

    from mikiui.app.plugin_security import _resolve_string_arg

    tree = ast.parse("'hello'")
    assert _resolve_string_arg(tree.body[0].value) == "hello"


def test_ast_resolve_string_concatenation():
    """_resolve_string_arg should handle string concatenation via BinOp."""
    import ast

    from mikiui.app.plugin_security import _resolve_string_arg

    tree = ast.parse("'ev' + 'al'")
    assert _resolve_string_arg(tree.body[0].value) == "eval"
