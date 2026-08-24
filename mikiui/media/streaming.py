"""Streaming media manager for MikiUI.

Manages named in-memory media streams that can be published to and subscribed
from via async generators producing Server-Sent Event (SSE) ready dicts.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any


def sse_chunk(payload: dict[str, Any]) -> dict[str, Any]:
    """Return an SSE-ready message dict for an arbitrary payload.

    Args:
        payload: Any JSON-serializable dict to send as the event data.

    Returns:
        A dict shaped like ``{"event": "message", "data": payload}``.
    """
    return {"event": "message", "data": payload}


class StreamingManager:
    """Manage named media streams that can be published to and subscribed from.

    Each stream has a unique id and an internal asyncio queue. Publishers push
    chunks; subscribers receive them as SSE-ready dicts via an async generator.
    """

    def __init__(self) -> None:
        self._streams: dict[str, asyncio.Queue[Any]] = {}
        self._counter = 0

    def create_stream(self, name: str) -> str:
        """Create a new stream and return its unique id.

        Args:
            name: A human-readable name for the stream (stored for reference).

        Returns:
            A unique stream id string.
        """
        self._counter += 1
        stream_id = f"{name}-{self._counter}"
        self._streams[stream_id] = asyncio.Queue()
        return stream_id

    def publish(self, stream_id: str, chunk: dict[str, Any]) -> None:
        """Publish a chunk to a stream.

        Args:
            stream_id: The id returned by ``create_stream``.
            chunk: A JSON-serializable dict representing a media chunk.
        """
        queue = self._streams.get(stream_id)
        if queue is None:
            raise KeyError(f"Unknown stream id: {stream_id}")
        queue.put_nowait(chunk)

    async def subscribe(self, stream_id: str) -> AsyncGenerator[dict[str, Any]]:
        """Subscribe to a stream, yielding chunks as SSE-ready dicts.

        Args:
            stream_id: The id returned by ``create_stream``.

        Yields:
            Dicts shaped like ``{"event": "chunk", "data": chunk}``.

        Raises:
            KeyError: If the stream id is unknown.
        """
        queue = self._streams.get(stream_id)
        if queue is None:
            raise KeyError(f"Unknown stream id: {stream_id}")
        while True:
            chunk = await queue.get()
            yield {"event": "chunk", "data": chunk}

    def active_streams(self) -> list[str]:
        """Return the list of currently active stream ids."""
        return list(self._streams.keys())
