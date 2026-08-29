"""Helper module for ``mikiui dev`` with reload support.

When ``--reload`` is active uvicorn re-imports this module in the worker
process on each file change.  The CLI sets the ``MIKIUI_APP_SPEC`` environment
variable (inherited by uvicorn workers) so that :func:`app_factory` always
points at the right user app, even after a reload.
"""

from __future__ import annotations

import importlib
import os
from typing import Any

from ..backend import create_app


def app_factory() -> Any:
    """Build and return the FastAPI ASGI app for the current ``APP_SPEC``.

    The spec is read from the ``MIKIUI_APP_SPEC`` environment variable at call
    time, so reloads pick up any changes to the variable's value too.
    """
    spec = os.environ.get("MIKIUI_APP_SPEC", "")
    if not spec:
        raise RuntimeError(
            "MIKIUI_APP_SPEC environment variable is not set. "
            "This should be set by the `mikiui dev` command."
        )

    module_name, _, attr = spec.partition(":")
    if not module_name:
        raise RuntimeError(
            f"Invalid MIKIUI_APP_SPEC: {spec!r}. "
            "Expected format: 'module.path:attr'"
        )

    try:
        mod = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f"Cannot import module '{module_name}'. "
            "Make sure your app file exists and has no syntax errors."
        ) from exc

    try:
        miki_app = getattr(mod, attr or "app")
    except AttributeError as exc:
        raise RuntimeError(
            f"Module '{module_name}' has no attribute '{attr or 'app'}'. "
            "Check your --app spec."
        ) from exc

    return create_app(miki_app)
