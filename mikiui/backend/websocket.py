"""WebSocket support for MikiUI.

Helper to mount a JSON WebSocket endpoint on a FastAPI app. Used for live
updates (media streaming, realtime widgets) without polling.
"""

from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, WebSocket, WebSocketDisconnect


class ConnectionManager:
    """Tracks active WebSocket connections for broadcast."""

    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: Any) -> None:
        for ws in list(self.active):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(ws)


def mount_websocket(router: APIRouter, path: str, handler: Callable) -> None:
    """Mount ``handler(websocket, manager)`` at ``path`` on ``router``."""

    manager = ConnectionManager()

    async def endpoint(ws: WebSocket) -> None:
        await manager.connect(ws)
        try:
            await handler(ws, manager)
        except WebSocketDisconnect:
            manager.disconnect(ws)

    router.add_api_websocket_route(path, endpoint)
