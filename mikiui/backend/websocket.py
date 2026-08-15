"""WebSocket support for MikiUI.

Helper to mount a JSON WebSocket endpoint on a FastAPI app with security
controls: Origin validation, optional auth, connection limits, and message
size limits.
"""

from __future__ import annotations

import secrets
from typing import Any, Callable

from fastapi import APIRouter, WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Tracks active WebSocket connections for broadcast."""

    def __init__(
        self,
        *,
        max_connections_per_user: int = 5,
        max_connections_per_ip: int = 10,
        max_message_size: int = 1024 * 1024,
        allowed_origins: list[str] | None = None,
        validate_token: Callable[[str], str | None] | None = None,
    ) -> None:
        self.active: list[WebSocket] = []
        self._max_connections_per_user = max_connections_per_user
        self._max_connections_per_ip = max_connections_per_ip
        self._max_message_size = max_message_size
        self._allowed_origins = set(allowed_origins or [])
        self._validate_token = validate_token
        self._user_counts: dict[str, int] = {}
        self._ip_counts: dict[str, int] = {}

    async def connect(self, ws: WebSocket) -> str | None:
        """Accept a WebSocket connection after security checks.

        Returns the authenticated user_id, or ``None`` if connection was
        rejected.
        """
        origin = ws.headers.get("origin", "")
        if self._allowed_origins and origin not in self._allowed_origins:
            await ws.close(code=4008, reason="Origin not allowed")
            return None

        ip = ws.client.host if ws.client else "unknown"
        if self._ip_counts.get(ip, 0) >= self._max_connections_per_ip:
            await ws.close(code=4009, reason="Connection limit per IP exceeded")
            return None

        token = ws.query_params.get("token") or ws.headers.get("Authorization", "").replace("Bearer ", "")
        user_id = None
        if self._validate_token:
            user_id = self._validate_token(token) if token else None
            if token and not user_id:
                await ws.close(code=4007, reason="Unauthorized")
                return None

        if user_id and self._user_counts.get(user_id, 0) >= self._max_connections_per_user:
            await ws.close(code=4009, reason="Connection limit per user exceeded")
            return None

        await ws.accept()
        self.active.append(ws)

        if user_id:
            self._user_counts[user_id] = self._user_counts.get(user_id, 0) + 1
        self._ip_counts[ip] = self._ip_counts.get(ip, 0) + 1

        ws.state.mikiui_user_id = user_id
        ws.state.mikiui_ip = ip
        return user_id

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)
        user_id = getattr(ws.state, "mikiui_user_id", None)
        ip = getattr(ws.state, "mikiui_ip", None)
        if user_id and user_id in self._user_counts:
            self._user_counts[user_id] -= 1
            if self._user_counts[user_id] <= 0:
                del self._user_counts[user_id]
        if ip and ip in self._ip_counts:
            self._ip_counts[ip] -= 1
            if self._ip_counts[ip] <= 0:
                del self._ip_counts[ip]

    async def broadcast(self, message: Any) -> None:
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(ws)

    async def send(self, ws: WebSocket, message: Any) -> None:
        try:
            await ws.send_json(message)
        except Exception:
            self.disconnect(ws)

    def get_user_id(self, ws: WebSocket) -> str | None:
        return getattr(ws.state, "mikiui_user_id", None)


def mount_websocket(
    router: APIRouter,
    path: str,
    handler: Callable,
    *,
    manager: ConnectionManager | None = None,
    max_message_size: int | None = None,
) -> None:
    """Mount ``handler(websocket, manager)`` at ``path`` on ``router``.

    Parameters
    ----------
    router:
        FastAPI router to mount the WebSocket route on.
    path:
        URL path for the WebSocket endpoint.
    handler:
        Async callable receiving ``(websocket, manager)``.
    manager:
        Optional pre-configured :class:`ConnectionManager`.  A new one is
        created when omitted.
    max_message_size:
        Maximum message size in bytes.  Defaults to the manager's limit.
    """
    if manager is None:
        manager = ConnectionManager()
    if max_message_size is not None:
        manager._max_message_size = max_message_size

    async def endpoint(ws: WebSocket) -> None:
        user_id = await manager.connect(ws)
        if user_id is None and ws.headers.get("authorization"):
            return
        try:
            await handler(ws, manager)
        except WebSocketDisconnect:
            manager.disconnect(ws)

    router.add_api_websocket_route(path, endpoint)
