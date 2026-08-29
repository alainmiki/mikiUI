"""Request ID middleware for distributed tracing.

Generates a unique request ID for every incoming request and propagates it
through response headers. Supports inbound ``X-Request-ID`` header for
cross-service trace continuity.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

_REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Assigns a unique ID to every request for logging/tracing.

    The ID is stored on ``request.state.request_id`` and echoed back in
    the ``X-Request-ID`` response header.  If the incoming request already
    carries an ``X-Request-ID`` header, it is preserved (for cross-service
    tracing).
    """

    def __init__(
        self,
        app: Any,
        header_name: str = _REQUEST_ID_HEADER,
    ) -> None:
        super().__init__(app)
        self._header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Any:
        request_id = request.headers.get(self._header_name) or uuid.uuid4().hex[:16]
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[self._header_name] = request_id
        return response


__all__ = ["RequestIDMiddleware"]
