"""Server-Sent Events (SSE) support for MikiUI.

Helper that yields an SSE response from an async generator of messages, used
for streaming updates (media progress, logs, notifications) to the browser.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from fastapi.responses import StreamingResponse


def sse_response(generator: AsyncGenerator[Any]) -> StreamingResponse:
    async def event_stream():
        async for message in generator:
            if isinstance(message, dict):
                data = "\n".join(f"{k}: {v}" for k, v in message.items())
            else:
                data = str(message)
            yield f"data: {data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
