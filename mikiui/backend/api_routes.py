"""Additional API routes (health, metadata)."""

from __future__ import annotations

from fastapi import APIRouter, Request


def add_api_routes(router: APIRouter, title: str = "MikiUI App") -> None:
    """Register utility endpoints (health check, app metadata)."""

    @router.get("/_miki/health", tags=["miki"])
    async def health() -> dict:
        return {"status": "ok", "app": title}

    @router.get("/_miki/meta", tags=["miki"])
    async def meta() -> dict:
        return {"name": title, "framework": "mikiui"}

    @router.post("/_miki/api/theme", tags=["miki"])
    async def set_theme(request: Request) -> dict:
        body = await request.json()
        theme_name = body.get("theme")
        app = request.app.state.miki_app
        if theme_name and theme_name in app.theme_registry.list_all():
            app.set_theme(theme_name)
            return {"status": "ok", "theme": theme_name}
        return {"status": "error", "message": f"Unknown theme: {theme_name}"}
