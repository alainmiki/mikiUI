"""Additional API routes (health, metadata)."""

from __future__ import annotations

from fastapi import APIRouter


def add_api_routes(router: APIRouter, title: str = "MikiUI App") -> None:
    """Register utility endpoints (health check, app metadata)."""

    @router.get("/_miki/health", tags=["miki"])
    async def health() -> dict:
        return {"status": "ok", "app": title}

    @router.get("/_miki/meta", tags=["miki"])
    async def meta() -> dict:
        return {"name": title, "framework": "mikiui"}
