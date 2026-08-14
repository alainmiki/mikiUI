"""Helper module for `mikiui dev` with reload support.

When ``--reload`` is active uvicorn re-imports the target string in the worker
process.  This module exposes an :func:`app_factory` ASGI factory that reads the
user-specified app path (``module:attr``) from :data:`APP_SPEC` and wraps it in
a FastAPI app via :func:`~mikiui.backend.create_app`.

The CLI sets ``APP_SPEC`` before launching uvicorn; on each reload the reimported
module retains that value, so the factory always points at the right user app.
"""

from __future__ import annotations

import importlib
from typing import Any, Callable

from ..backend import create_app

#: User-provided app spec (``"module.path:attr"``), set by the ``dev`` command.
APP_SPEC: str = "mikiui.examples.demo:app"

#: Factory used to wrap a :class:`~mikiui.app.MikiApp` in a FastAPI ASGI app.
CREATE_APP: Callable[..., Any] = create_app


def app_factory() -> Any:
    """Build and return the FastAPI ASGI app for the current ``APP_SPEC``."""
    module_name, _, attr = APP_SPEC.partition(":")
    mod = importlib.import_module(module_name)
    miki_app = getattr(mod, attr or "app")
    return CREATE_APP(miki_app)
