"""Chaquopy Python bridge for on-device mobile mode.

This module provides the Python-side bridge that connects JavaScript calls
from the Android WebView directly to MikiApp route handlers via Chaquopy's
@JavascriptInterface.

No HTTP server, no sockets — direct function invocation with <1ms latency.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any


class ChaquopyBridge:
    """Exposed to Android WebView via @JavascriptInterface.

    This bridge resolves routes directly from the MikiApp and invokes
    handlers without any HTTP layer. The result is returned as a JSON
    string to the JavaScript caller.
    """

    def __init__(self, app: Any) -> None:
        self._app = app

    def call(self, method: str, path: str, data_json: str) -> str:
        """Handle a backend call from JavaScript.

        Parameters
        ----------
        method:
            HTTP method (GET, POST, etc.) — used for logging/validation.
        path:
            Route path (e.g., ``/api/users``).
        data_json:
            JSON-encoded request body (or empty string for GET).

        Returns
        -------
        JSON-encoded response string.
        """
        try:
            data = json.loads(data_json) if data_json else None
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON in request body", "status": 400})

        try:
            route = self._app.get_route(path)
        except Exception:
            route = None

        if route is None:
            return json.dumps({"error": f"No route: {path}", "status": 404})

        try:
            result = self._invoke_route(route, data)
            return self._format_response(result)
        except Exception as exc:
            return json.dumps({"error": str(exc), "status": 500})

    def _invoke_route(self, route: Any, data: Any) -> Any:
        """Invoke a route handler with the given data."""
        import inspect

        handler = route.handler
        sig = inspect.signature(handler)
        params = list(sig.parameters.keys())

        kwargs: dict[str, Any] = {}

        # Check if handler accepts ctx/request as first param
        if params and params[0] in ("ctx", "request"):
            from ...routes import Ctx
            # Build a minimal Ctx for on-device mode
            # request is None since there's no HTTP request
            ctx = Ctx(None, self._app, {})
            kwargs[params[0]] = ctx

        # Add data as kwargs for POST/PUT/PATCH
        if data and isinstance(data, dict):
            for key, value in data.items():
                if key in params:
                    kwargs[key] = value

        # Invoke handler
        if asyncio.iscoroutinefunction(handler):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # We're inside an async context, use run_coroutine_threadsafe
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        result = pool.submit(asyncio.run, handler(**kwargs)).result()
                else:
                    result = loop.run_until_complete(handler(**kwargs))
            except RuntimeError:
                # No event loop, create one
                result = asyncio.run(handler(**kwargs))
        else:
            result = handler(**kwargs)

        return result

    def _format_response(self, result: Any) -> str:
        """Format the handler result as a JSON response."""
        if isinstance(result, tuple):
            body, status_code = result if len(result) == 2 else (result[0], 200)
        else:
            body = result
            status_code = 200

        if isinstance(body, dict):
            body["status"] = body.get("status", status_code)
            return json.dumps(body)
        return json.dumps({"data": body, "status": status_code})


_bridge_instance: ChaquopyBridge | None = None


def get_bridge(app: Any) -> ChaquopyBridge:
    """Get or create the singleton bridge instance.

    This is the function exposed to Kotlin via Chaquopy.
    """
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = ChaquopyBridge(app)
    return _bridge_instance


def reset_bridge() -> None:
    """Reset the bridge instance (for testing)."""
    global _bridge_instance
    _bridge_instance = None


__all__ = ["ChaquopyBridge", "get_bridge", "reset_bridge"]
