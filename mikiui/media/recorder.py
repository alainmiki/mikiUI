"""In-memory recording tracker for MikiUI.

Tracks recording sessions with simple metadata, kept in memory only.
"""

from __future__ import annotations

import datetime
from typing import Any


class Recorder:
    """Track recordings (start/stop/list) entirely in memory.

    Each recording stores metadata: id, name, started_at, status, stopped_at.
    """

    def __init__(self) -> None:
        self._recordings: dict[str, dict[str, Any]] = {}
        self._counter = 0

    def start(self, name: str) -> str:
        """Start a new recording and return its id.

        Args:
            name: A human-readable name for the recording.

        Returns:
            The unique recording id.
        """
        self._counter += 1
        rec_id = f"rec-{self._counter}"
        self._recordings[rec_id] = {
            "id": rec_id,
            "name": name,
            "started_at": datetime.datetime.now(),
            "status": "recording",
            "stopped_at": None,
        }
        return rec_id

    def stop(self, rec_id: str) -> None:
        """Stop a recording, marking its status and stop time.

        Args:
            rec_id: The id returned by ``start``.

        Raises:
            KeyError: If the recording id is unknown.
        """
        rec = self._recordings.get(rec_id)
        if rec is None:
            raise KeyError(f"Unknown recording id: {rec_id}")
        rec["status"] = "stopped"
        rec["stopped_at"] = datetime.datetime.now()

    def list_recordings(self) -> list[dict[str, Any]]:
        """Return a list of all recording metadata dicts."""
        return list(self._recordings.values())

    def get(self, rec_id: str) -> dict[str, Any] | None:
        """Return metadata for a recording id, or None if unknown.

        Args:
            rec_id: The id returned by ``start``.

        Returns:
            The recording metadata dict, or None.
        """
        return self._recordings.get(rec_id)
