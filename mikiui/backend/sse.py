"""Server-Sent Events (SSE) support for MikiUI.

Helper that yields an SSE response from an async generator of messages, used
for streaming updates (media progress, logs, notifications) to the browser.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any, Protocol

from fastapi.responses import StreamingResponse


class StreamProtocol(Protocol):
    async def send(self, message: Any) -> None: ...


class SSEManager:
    """Manages active SSE streams and broadcasts messages."""

    def __init__(self, buffer_size: int = 100) -> None:
        self.active_streams: list[StreamProtocol] = []
        self._buffer: list[tuple[str, Any]] = []
        self._buffer_size = buffer_size
        self._counter = 0

    def register(self, stream: StreamProtocol) -> None:
        self.active_streams.append(stream)

    def remove_stream(self, stream: StreamProtocol) -> None:
        if stream in self.active_streams:
            self.active_streams.remove(stream)

    async def broadcast(self, message: Any) -> str:
        self._counter += 1
        event_id = str(self._counter)
        entry = (event_id, message)
        self._buffer.append(entry)
        if len(self._buffer) > self._buffer_size:
            self._buffer.pop(0)
        to_remove: list[StreamProtocol] = []
        for stream in self.active_streams:
            try:
                await stream.send(message)
            except Exception:
                to_remove.append(stream)
        for stream in to_remove:
            self.remove_stream(stream)
        return event_id

    def get_since(self, last_event_id: str | None) -> list[tuple[str, Any]]:
        if last_event_id is None:
            return []
        try:
            target = int(last_event_id)
        except (ValueError, TypeError):
            return []
        return [(eid, msg) for eid, msg in self._buffer if int(eid) > target]

    async def close_all(self) -> None:
        self.active_streams.clear()


def sse_response(generator: AsyncGenerator[Any], last_event_id: str | None = None) -> StreamingResponse:
    """Create an SSE StreamingResponse from an async generator.

    Each message from the generator can be:
    - A plain value: sent as ``data: <value>\\n\\n``
    - A dict with an ``event`` key: sent as a named event
      (``event: <name>\\ndata: <value>\\n\\n``)
    - A dict with just a ``data`` key: formatted as ``data: <value>\\n\\n``
    - Any other dict: each key/value pair becomes a field

    Parameters
    ----------
    generator:
        Async generator yielding SSE messages.
    last_event_id:
        If provided, included as the ``Last-Event-Id`` response header so
        clients can resume from a specific point.
    """
    async def event_stream():
        try:
            async for message in generator:
                if isinstance(message, dict):
                    lines = []
                    if "event" in message:
                        lines.append(f"event: {message['event']}")
                    if "id" in message:
                        lines.append(f"id: {message['id']}")
                    if "data" in message:
                        lines.append(f"data: {message['data']}")
                    # Include any other keys as SSE fields
                    for k, v in message.items():
                        if k not in ("event", "id", "data"):
                            lines.append(f"{k}: {v}")
                    if lines:
                        yield "\n".join(lines) + "\n\n"
                    else:
                        yield "data: \n\n"
                else:
                    data = str(message)
                    yield f"data: {data}\n\n"
        except BaseException:
            pass

    headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    if last_event_id:
        headers["Last-Event-Id"] = last_event_id

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=headers,
    )
