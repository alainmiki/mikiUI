"""WebSocket support for MikiUI.

Helper to mount a JSON WebSocket endpoint on a FastAPI app with security
controls: Origin validation, optional auth, connection limits, and message
size limits.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketAuthHelper:
    """Integrates WebSocket connections with MikiUI auth strategies.

    Supports session cookies, Bearer tokens, and query-param tokens.
    Uses the app's registered auth strategies for validation.

    Usage::

        auth_helper = WebSocketAuthHelper(app)
        user_id = await auth_helper.authenticate(ws)
    """

    def __init__(self, app: Any) -> None:
        self._app = app

    async def authenticate(self, ws: WebSocket) -> Any | None:
        """Authenticate a WebSocket connection.

        Returns the user object from the auth strategy, or None for
        unauthenticated connections.  Preference order:
        1. Session cookie (mikiui_session)
        2. Authorization: Bearer <token> header
        3. ?token=<token> query param
        """
        # Extract token from various sources
        token = (
            ws.query_params.get("token")
            or ws.cookies.get("mikiui_session")
            or ws.headers.get("Authorization", "").replace("Bearer ", "").strip()
            or None
        )

        if not token:
            return None

        # Try session strategy first, then any strategy that can validate
        for strategy_name in ("session", "jwt", "api_key"):
            strategy = self._app.get_auth_strategy(strategy_name)
            if strategy is None:
                continue
            try:
                if hasattr(strategy, "validate"):
                    user = strategy.validate(ws)
                    if user is not None:
                        return user
                elif callable(strategy):
                    user = strategy(token)
                    if user is not None:
                        return user
            except Exception:
                continue
        return None

    def extract_token(self, ws: WebSocket) -> str | None:
        """Extract the raw token from a WebSocket connection."""
        return (
            ws.query_params.get("token")
            or ws.cookies.get("mikiui_session")
            or ws.headers.get("Authorization", "").replace("Bearer ", "").strip()
            or None
        )


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
        # Room/channel support
        self._rooms: dict[str, set[WebSocket]] = {}
        self._ws_rooms: dict[WebSocket, set[str]] = {}

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
        auth_header = ws.headers.get("Authorization", "")
        user_id = None
        if self._validate_token:
            user_id = self._validate_token(token) if token else None
            if token and not user_id:
                logger.warning("WebSocket connection rejected: invalid token")
                await ws.close(code=4007, reason="Unauthorized")
                return None
        elif auth_header:
            logger.warning(
                "WebSocket auth header received but no token validator configured"
            )
            await ws.close(code=4007, reason="Auth header without validator")
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
        # Clean up rooms
        self.leave_all_rooms(ws)
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

    async def _send_pending(self, message: Any) -> None:
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(ws)

    async def heartbeat(self) -> None:
        for ws in list(self.active):
            try:
                await ws.send_text("ping")
            except Exception:
                self.disconnect(ws)

    def get_user_id(self, ws: WebSocket) -> str | None:
        return getattr(ws.state, "mikiui_user_id", None)

    def get_connection_count(self) -> int:
        """Return the number of active WebSocket connections."""
        return len(self.active)

    async def send(self, ws: WebSocket, message: Any) -> None:
        """Send a text message to a single WebSocket connection."""
        await ws.send_text(message if isinstance(message, str) else str(message))

    async def ping(self) -> None:
        """Send a ping message to all active connections."""
        for ws in list(self.active):
            try:
                await ws.send_text("ping")
            except Exception:
                self.disconnect(ws)

    # -- Room / channel support -----------------------------------------------

    def join_room(self, ws: WebSocket, room: str) -> None:
        """Add a connection to a room."""
        if room not in self._rooms:
            self._rooms[room] = set()
        self._rooms[room].add(ws)
        if ws not in self._ws_rooms:
            self._ws_rooms[ws] = set()
        self._ws_rooms[ws].add(room)

    def leave_room(self, ws: WebSocket, room: str) -> None:
        """Remove a connection from a room."""
        if room in self._rooms:
            self._rooms[room].discard(ws)
            if not self._rooms[room]:
                del self._rooms[room]
        if ws in self._ws_rooms:
            self._ws_rooms[ws].discard(room)
            if not self._ws_rooms[ws]:
                del self._ws_rooms[ws]

    def leave_all_rooms(self, ws: WebSocket) -> None:
        """Remove a connection from all rooms it has joined."""
        rooms = self._ws_rooms.pop(ws, set())
        for room in rooms:
            if room in self._rooms:
                self._rooms[room].discard(ws)
                if not self._rooms[room]:
                    del self._rooms[room]

    def get_room_connections(self, room: str) -> list[WebSocket]:
        """Return all connections in a room."""
        return list(self._rooms.get(room, set()))

    def get_user_rooms(self, ws: WebSocket) -> list[str]:
        """Return all rooms a connection has joined."""
        return list(self._ws_rooms.get(ws, set()))

    async def broadcast_to_room(self, room: str, message: Any, exclude: WebSocket | None = None) -> None:
        """Send a JSON message to all connections in a room."""
        for ws in list(self._rooms.get(room, set())):
            if ws is exclude:
                continue
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(ws)
                self.leave_all_rooms(ws)

    async def broadcast_to_user(self, user_id: str, message: Any) -> None:
        """Send a JSON message to all connections belonging to a user."""
        for ws in list(self.active):
            if getattr(ws.state, "mikiui_user_id", None) == user_id:
                try:
                    await ws.send_json(message)
                except Exception:
                    self.disconnect(ws)

    def get_room_count(self, room: str) -> int:
        """Return the number of connections in a room."""
        return len(self._rooms.get(room, set()))

    def get_connection_info(self, ws: WebSocket) -> dict[str, Any]:
        """Return info about a connection (user_id, ip, rooms)."""
        return {
            "user_id": getattr(ws.state, "mikiui_user_id", None),
            "ip": getattr(ws.state, "mikiui_ip", None),
            "rooms": self.get_user_rooms(ws),
        }


def mount_websocket(
    router: APIRouter,
    path: str,
    handler: Callable[[WebSocket, ConnectionManager], Any],
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
        if user_id is None:
            # Connection was either rejected (already closed) or accepted
            # without authentication. Don't proceed if an auth header was
            # sent but no validator is configured — connect() closes in that case.
            if ws.headers.get("authorization"):
                return
            if manager._validate_token:
                # Token was required but invalid/rejected; connection already closed
                return
        try:
            await _size_limited_handler(ws, manager, handler, manager._max_message_size)
        except WebSocketDisconnect:
            manager.disconnect(ws)

    router.add_api_websocket_route(path, endpoint)


async def _size_limited_handler(
    ws: WebSocket,
    manager: ConnectionManager,
    handler: Callable[[WebSocket, ConnectionManager], Any],
    max_size: int,
) -> None:
    """Wrap *handler* to reject messages exceeding *max_size* bytes."""
    import json as _json

    original_receive = ws.receive_text

    async def _checked_receive_text() -> str:
        data = await original_receive()
        if len(data.encode("utf-8")) > max_size:
            await ws.close(code=1009, reason="Message too large")
            raise WebSocketDisconnect()
        return data

    async def _checked_receive_json() -> Any:
        raw = await _checked_receive_text()
        if len(raw.encode("utf-8")) > max_size:
            await ws.close(code=1009, reason="Message too large")
            raise WebSocketDisconnect()
        return _json.loads(raw)

    ws.receive_text = _checked_receive_text  # type: ignore[method-assign]
    ws.receive_json = _checked_receive_json  # type: ignore[method-assign,assignment]
    await handler(ws, manager)


def create_webrtc_signaling_handler(manager: ConnectionManager) -> Callable:
    """Create a WebRTC signaling handler that relays SDP/ICE between peers.

    WebRTC runs entirely in the WebView JavaScript context. Python only
    relays JSON signaling messages between peers in the same room.

    Usage::

        from mikiui.backend.websocket import ConnectionManager, create_webrtc_signaling_handler

        manager = ConnectionManager()

        @app.websocket("/ws/webrtc/{room_id}")
        async def webrtc_signaling(ws: WebSocket, room_id: str):
            handler = create_webrtc_signaling_handler(manager)
            await handler(ws, room_id)

    Parameters
    ----------
    manager:
        The ConnectionManager instance to track connections.

    Returns
    -------
    An async handler function suitable for a FastAPI WebSocket endpoint.
    """
    import json

    async def handler(ws: WebSocket, room_id: str) -> None:
        await ws.accept()
        manager.join_room(ws, f"webrtc-{room_id}")
        logger.debug("WebRTC peer connected to room %s", room_id)

        try:
            while True:
                raw = await ws.receive_text()
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                # Validate signaling message structure
                msg_type = msg.get("type")
                if msg_type not in ("offer", "answer", "ice-candidate", "join", "leave"):
                    continue

                # Relay to all other peers in the room
                await manager.broadcast_to_room(
                    f"webrtc-{room_id}",
                    msg,
                    exclude=ws,
                )
        except WebSocketDisconnect:
            pass
        finally:
            manager.leave_room(ws, f"webrtc-{room_id}")
            logger.debug("WebRTC peer disconnected from room %s", room_id)

    return handler


__all__ = [
    "ConnectionManager",
    "WebSocketAuthHelper",
    "mount_websocket",
    "create_webrtc_signaling_handler",
]
