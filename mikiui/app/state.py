"""Shared application state.

``AppState`` is the server-side store handlers read/write for optimistic and
stateful interactions. It is a dict subclass so existing dict code keeps working
and it can later be backed by PostgreSQL/Redis (see PRD) without API changes.
"""

from __future__ import annotations

from typing import Any


class AppState(dict):
    """Server-side shared state for a MikiUI app."""

    def get_or_default(self, key: str, default: Any = None) -> Any:
        return self.get(key, default)

    def increment(self, key: str, step: int = 1) -> int:
        self[key] = int(self.get(key, 0)) + step
        return int(self[key])

    def decrement(self, key: str, step: int = 1) -> int:
        self[key] = int(self.get(key, 0)) - step
        return int(self[key])
