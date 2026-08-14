"""MikiUI CLI package."""

from __future__ import annotations

from .commands import cli

# `pyproject.toml` exposes `mikiui = "mikiui.cli:app"`.
app = cli

__all__ = ["cli", "app"]
