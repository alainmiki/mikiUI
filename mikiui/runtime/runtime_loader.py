"""Framework runtime loader.

Selects the JS runtime scripts to inject into pages. The DEFAULT is the bundled,
real HTMX + Alpine.js libraries served locally from ``mikiui/runtime/`` (files
``htmx.min.js`` and ``alpine.min.js``), so apps work fully offline — essential
for the native desktop window, which often cannot reach a CDN. ``mode="cdn"``
upgrades to the same libraries from unpkg when internet is available.
"""

from __future__ import annotations


def runtime_scripts(mode: str = "local") -> list[str]:
    if mode == "cdn":
        return [
            "https://unpkg.com/htmx.org@2.0.3",
            "https://unpkg.com/alpinejs@3.14.1/dist/cdn.min.js",
            "/_miki/runtime/miki_ui.js",
            "/_miki/runtime/htmx_runtime.js",
            "/_miki/runtime/alpine_runtime.js",
            "/_miki/runtime/history_router.js",
        ]
    # Offline-first: real HTMX + Alpine served locally by the backend.
    # Order matters: HTMX loads first, then Alpine.js (depends on being on page),
    # then the runtime wrappers, then MikiUI's own widget handlers.
    return [
        "/_miki/runtime/htmx.min.js",
        "/_miki/runtime/htmx_runtime.js",
        "/_miki/runtime/alpine.min.js",
        "/_miki/runtime/alpine_runtime.js",
        "/_miki/runtime/miki_ui.js",
        "/_miki/runtime/history_router.js",
    ]