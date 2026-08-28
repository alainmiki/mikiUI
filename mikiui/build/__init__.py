"""MikiUI build system (web + desktop packaging, asset optimization).

Public surface used by the CLI (``mikiui build``, ``mikiui desktop``) and
``app.run(desktop=True)``:

* :func:`build_web` — produce a web build (fullstack or separate mode).
* :func:`build_desktop` — produce a desktop (pywebview) build.
* :func:`optimize` — minify/optimize bundled runtime assets.
* :func:`run_desktop` — launch the app as a native window (see
  :mod:`mikiui.build.desktop_build`).

Styling builds (Tailwind + DaisyUI) live in :mod:`mikiui.build.tailwind`.
"""

from __future__ import annotations

from .desktop_build import build_desktop, run_desktop
from .optimizer import optimize
from .tailwind import build_css, register_built_theme
from .web_build import build_web

__all__ = [
    "build_web",
    "build_desktop",
    "optimize",
    "run_desktop",
    "build_css",
    "register_built_theme",
]
