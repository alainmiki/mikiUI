"""Notification plugin for MikiUI.

Provides in-memory notification queue per user session with support for
info, success, warning, and error types. Includes an Alpine.js component
for toast rendering, WebSocket support for real-time push notifications,
and persistence to session storage.

Usage:
    from mikiui import MikiApp
    from mikiui_app_plugins import NotificationPlugin

    app = MikiApp(title="My App")
    app.use(NotificationPlugin())

    # In a route handler
    @app.route("/action")
    def do_something(ctx):
        ctx.app.notifications.notify("user-1", "Action completed!", type="success")
        return Div("Done")
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Callable

from fastapi import WebSocket, WebSocketDisconnect

from mikiui.app.plugins import Plugin

logger = logging.getLogger(__name__)


@dataclass
class Notification:
    """A single notification message.

    Attributes:
        id: Unique notification identifier.
        user_id: Target user ID (or ``"*"`` for broadcast).
        message: Notification text content.
        type: Notification type: info, success, warning, error.
        duration: Auto-dismiss duration in milliseconds (0 = sticky).
        created_at: Unix timestamp of creation.
        read: Whether the notification has been read.
    """

    id: str
    user_id: str
    message: str
    type: str = "info"
    duration: int = 5000
    created_at: float = field(default_factory=time.time)
    read: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "type": self.type,
            "duration": self.duration,
            "created_at": self.created_at,
            "read": self.read,
        }


class NotificationQueue:
    """In-memory notification queue per user session.

    Thread-safe for basic use. For production with multiple workers,
    consider Redis or a database-backed store.
    """

    def __init__(self, max_per_user: int = 100) -> None:
        self._queues: dict[str, deque[Notification]] = defaultdict(deque)
        self._max_per_user = max_per_user
        self._listeners: dict[str, list[Callable]] = defaultdict(list)

    def enqueue(self, notification: Notification) -> None:
        """Add a notification to the queue.

        Parameters
        ----------
        notification:
            The notification to enqueue.
        """
        user_id = notification.user_id
        queue = self._queues[user_id]
        queue.append(notification)
        # Enforce max per user
        while len(queue) > self._max_per_user:
            queue.popleft()
        # Notify listeners
        for listener in self._listeners.get(user_id, []):
            try:
                listener(notification)
            except Exception:
                logger.exception("Notification listener failed.")

    def dequeue(self, user_id: str) -> Notification | None:
        """Pop the oldest unread notification for a user.

        Parameters
        ----------
        user_id:
            The user to dequeue notifications for.

        Returns
        -------
        Notification | None
            The oldest unread notification, or None.
        """
        queue = self._queues.get(user_id, deque())
        for i, notif in enumerate(queue):
            if not notif.read:
                notif.read = True
                return notif
        return None

    def peek(self, user_id: str, *, unread_only: bool = True) -> list[Notification]:
        """Peek at notifications without removing them.

        Parameters
        ----------
        user_id:
            The user to peek notifications for.
        unread_only:
            If True, only return unread notifications.

        Returns
        -------
        list[Notification]
            List of notifications matching the criteria.
        """
        queue = list(self._queues.get(user_id, deque()))
        if unread_only:
            return [n for n in queue if not n.read]
        return queue

    def mark_read(self, user_id: str, notification_id: str) -> None:
        """Mark a specific notification as read.

        Parameters
        ----------
        user_id:
            The user who owns the notification.
        notification_id:
            The notification ID to mark as read.
        """
        for notif in self._queues.get(user_id, deque()):
            if notif.id == notification_id:
                notif.read = True
                break

    def clear(self, user_id: str) -> None:
        """Clear all notifications for a user.

        Parameters
        ----------
        user_id:
            The user whose notifications to clear.
        """
        self._queues[user_id].clear()

    def add_listener(self, user_id: str, listener: Callable) -> None:
        """Add a listener for new notifications.

        Parameters
        ----------
        user_id:
            The user to listen for.
        listener:
            Callable receiving the new notification.
        """
        self._listeners[user_id].append(listener)

    def remove_listener(self, user_id: str, listener: Callable) -> None:
        """Remove a notification listener.

        Parameters
        ----------
        user_id:
            The user to stop listening for.
        listener:
            The listener to remove.
        """
        if listener in self._listeners.get(user_id, []):
            self._listeners[user_id].remove(listener)


class NotificationPlugin(Plugin):
    """Notification plugin for MikiUI.

    Provides an in-memory notification queue per user session with
    support for info, success, warning, and error notification types.

    Attributes:
        name: Plugin identifier.
        max_per_user: Maximum notifications to keep per user.
        default_duration: Default auto-dismiss duration in ms.
    """

    name = "notifications"
    depends_on = ["session"]

    def __init__(
        self,
        max_per_user: int = 100,
        default_duration: int = 5000,
        websocket_path: str = "/ws/notifications",
    ) -> None:
        """Initialize the notification plugin.

        Parameters
        ----------
        max_per_user:
            Maximum notifications to store per user.
        default_duration:
            Default auto-dismiss duration in milliseconds.
        websocket_path:
            Path for the WebSocket endpoint for real-time notifications.
        """
        self._queue = NotificationQueue(max_per_user=max_per_user)
        self.default_duration = default_duration
        self.websocket_path = websocket_path
        self._websocket_manager: Any = None

    def register(self, app: Any) -> None:
        """Register the notification plugin with the app."""
        app._notification_plugin = self
        app.notifications = self

    def configure(self, config: dict[str, Any]) -> None:
        """Configure notification defaults.

        Parameters
        ----------
        config:
            Configuration dict. Supported keys:
            - ``default_duration``: Default notification duration in ms.
            - ``max_per_user``: Max notifications per user.
        """
        if "default_duration" in config:
            self.default_duration = config["default_duration"]
        if "max_per_user" in config:
            self._queue._max_per_user = config["max_per_user"]

    def notify(
        self,
        user_id: str,
        message: str,
        type: str = "info",
        duration: int | None = None,
    ) -> Notification:
        """Create and enqueue a notification.

        Parameters
        ----------
        user_id:
            Target user ID. Use ``"*"`` for broadcast.
        message:
            Notification text.
        type:
            Notification type: ``"info"``, ``"success"``, ``"warning"``, ``"error"``.
        duration:
            Auto-dismiss duration in milliseconds. Defaults to plugin setting.

        Returns
        -------
        Notification
            The created notification.
        """
        if type not in ("info", "success", "warning", "error"):
            type = "info"
        notif = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            message=message,
            type=type,
            duration=duration if duration is not None else self.default_duration,
        )
        self._queue.enqueue(notif)
        logger.debug("Notification queued: [%s] %s: %s", type, user_id, message)
        return notif

    def broadcast(
        self, message: str, type: str = "info", duration: int | None = None
    ) -> None:
        """Broadcast a notification to all users.

        Parameters
        ----------
        message:
            Notification text.
        type:
            Notification type.
        duration:
            Auto-dismiss duration in milliseconds.
        """
        self.notify("*", message, type=type, duration=duration)

    def get_notifications(
        self, user_id: str, *, unread_only: bool = True
    ) -> list[dict[str, Any]]:
        """Get notifications for a user.

        Parameters
        ----------
        user_id:
            The user to get notifications for.
        unread_only:
            If True, only return unread notifications.

        Returns
        -------
        list[dict[str, Any]]
            List of notification dicts.
        """
        return [n.to_dict() for n in self._queue.peek(user_id, unread_only=unread_only)]

    def mark_read(self, user_id: str, notification_id: str) -> None:
        """Mark a notification as read.

        Parameters
        ----------
        user_id:
            The user who owns the notification.
        notification_id:
            The notification ID.
        """
        self._queue.mark_read(user_id, notification_id)

    def clear(self, user_id: str) -> None:
        """Clear all notifications for a user.

        Parameters
        ----------
        user_id:
            The user whose notifications to clear.
        """
        self._queue.clear(user_id)

    def backend_routes(self) -> list[dict[str, Any]]:
        """Return API route definitions for notification endpoints."""
        plugin = self

        async def list_notifications(request: Any) -> Any:
            user_id = request.cookies.get("mikiui_user_id", "anonymous")
            return {"notifications": plugin.get_notifications(user_id)}

        async def create_notification(request: Any) -> Any:
            body = await request.json()
            user_id = body.get("user_id", "anonymous")
            message = body.get("message", "")
            type_ = body.get("type", "info")
            duration = body.get("duration")
            notif = plugin.notify(user_id, message, type=type_, duration=duration)
            return {"notification": notif.to_dict()}

        async def mark_notification_read(request: Any) -> Any:
            body = await request.json()
            user_id = body.get("user_id", "anonymous")
            notif_id = body.get("notification_id", "")
            plugin.mark_read(user_id, notif_id)
            return {"status": "ok"}

        async def clear_notifications(request: Any) -> Any:
            body = await request.json()
            user_id = body.get("user_id", "anonymous")
            plugin.clear(user_id)
            return {"status": "ok"}

        return [
            {
                "path": "/api/notifications",
                "methods": ["GET"],
                "endpoint": list_notifications,
                "include_in_schema": True,
                "tags": ["notifications"],
            },
            {
                "path": "/api/notifications",
                "methods": ["POST"],
                "endpoint": create_notification,
                "include_in_schema": True,
                "tags": ["notifications"],
            },
            {
                "path": "/api/notifications/read",
                "methods": ["POST"],
                "endpoint": mark_notification_read,
                "include_in_schema": True,
                "tags": ["notifications"],
            },
            {
                "path": "/api/notifications/clear",
                "methods": ["POST"],
                "endpoint": clear_notifications,
                "include_in_schema": True,
                "tags": ["notifications"],
            },
        ]

    async def websocket_handler(self, websocket: WebSocket, manager: Any) -> None:
        """WebSocket handler for real-time notifications.

        Parameters
        ----------
        websocket:
            The WebSocket connection.
        manager:
            The ConnectionManager instance.
        """
        user_id = await manager.connect(websocket)
        if user_id is None:
            return
        try:
            # Send any pending notifications
            pending = self.get_notifications(user_id)
            if pending:
                await manager.send(
                    websocket, {"type": "notifications", "data": pending}
                )
            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    if message.get("action") == "ping":
                        await manager.send(websocket, {"type": "pong"})
                    elif message.get("action") == "mark_read":
                        notif_id = message.get("notification_id", "")
                        self.mark_read(user_id, notif_id)
                except json.JSONDecodeError:
                    pass
        except WebSocketDisconnect:
            manager.disconnect(websocket)

    def assets(self) -> list[str]:
        """Return notification frontend assets."""
        return [
            "mikiui_app_plugins/notifications.js",
        ]

    def on_shutdown(self) -> None:
        """Clean up notification queues on shutdown."""
        self._queue._queues.clear()
        self._queue._listeners.clear()
        logger.info("NotificationPlugin shut down.")


__all__ = ["NotificationPlugin", "NotificationQueue", "Notification"]
