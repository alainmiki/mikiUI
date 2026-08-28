"""Framework runtime loader.

Selects the JS runtime scripts to inject into pages. The DEFAULT is the bundled,
real HTMX + Alpine.js libraries served locally from ``mikiui/runtime/`` (files
``htmx.min.js`` and ``alpine.min.js``), so apps work fully offline — essential
for the native desktop window, which often cannot reach a CDN. ``mode="cdn"``
upgrades to the same libraries from unpkg when internet is available.
"""

from __future__ import annotations


def runtime_scripts(mode: str = "local") -> list[str]:
    # Widget JS modules in dependency order:
    # core utilities ? bridge layer ? individual widgets ? init registry.
    # The bridge (miki_bridge.js) loads after core.js but BEFORE widget
    # modules so that safe widget lookups and data-miki-on bindings are
    # available when inline handlers execute.
    widget_modules = [
        "/_miki/runtime/js/core.js",
        "/_miki/runtime/js/miki_bridge.js",
        "/_miki/runtime/js/mikieditorarea.js",
        "/_miki/runtime/js/mikiide.js",
        "/_miki/runtime/js/mikimdi.js",
        "/_miki/runtime/js/mikistackedpanel.js",
        "/_miki/runtime/js/mikidialog.js",
        "/_miki/runtime/js/mikimodal.js",
        "/_miki/runtime/js/mikitabs.js",
        "/_miki/runtime/js/mikidrawer.js",
        "/_miki/runtime/js/mikisplitview.js",
        "/_miki/runtime/js/mikidockablepanel.js",
        "/_miki/runtime/js/mikislider.js",
        "/_miki/runtime/js/mikidial.js",
        "/_miki/runtime/js/mikiprogress.js",
        "/_miki/runtime/js/mikiprogressdialog.js",
        "/_miki/runtime/js/mikicollapsible.js",
        "/_miki/runtime/js/mikiaccordion.js",
        "/_miki/runtime/js/mikidatagrid.js",
        "/_miki/runtime/js/mikikanban.js",
        "/_miki/runtime/js/mikichat.js",
        "/_miki/runtime/js/mikidropzone.js",
        "/_miki/runtime/js/mikicarousel.js",
        "/_miki/runtime/js/mikimessagebox.js",
        "/_miki/runtime/js/mikitoggle.js",
        "/_miki/runtime/js/mikisearchableselect.js",
        "/_miki/runtime/js/mikicontextwindow.js",
        "/_miki/runtime/js/mikimenubar.js",
        "/_miki/runtime/js/mikibottomsheet.js",
        "/_miki/runtime/js/mikibottomnav.js",
        "/_miki/runtime/js/mikichip.js",
        "/_miki/runtime/js/mikipressable.js",
        "/_miki/runtime/js/mikilazygrid.js",
        "/_miki/runtime/js/mikivirtuallist.js",
        "/_miki/runtime/js/mikiscrollview.js",
        "/_miki/runtime/js/init.js",
    ]

    if mode == "cdn":
        return [
            "https://unpkg.com/htmx.org@2.0.3",
            "https://unpkg.com/alpinejs@3.14.1/dist/cdn.min.js",
            *widget_modules,
            "/_miki/runtime/htmx_runtime.js",
            "/_miki/runtime/alpine_runtime.js",
            "/_miki/runtime/history_router.js",
        ]
    # Offline-first: real HTMX + Alpine served locally by the backend.
    # Order matters: HTMX loads first, then Alpine.js (depends on being on page),
    # then the runtime wrappers, then MikiUI's widget modules.
    return [
        "/_miki/runtime/htmx.min.js",
        "/_miki/runtime/htmx_runtime.js",
        "/_miki/runtime/alpine.min.js",
        "/_miki/runtime/alpine_runtime.js",
        *widget_modules,
        "/_miki/runtime/history_router.js",
    ]
