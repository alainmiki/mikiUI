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

#: User-provided app spec (``"module.path:attr"``), set via env var by the CLI.
APP_SPEC: str = os.environ.get("MIKIUI_APP_SPEC", "mikiui.examples.demo:app")

#: Factory used to wrap a :class:`~mikiui.app.MikiApp` in a FastAPI ASGI app.
CREATE_APP = create_app


def app_factory() -> Any:
    """Build and return the FastAPI ASGI app for the current ``APP_SPEC``.

    The spec is read from the ``MIKIUI_APP_SPEC`` environment variable at call
    time, so reloads pick up any changes to the variable's value too.
    """
    spec = os.environ.get("MIKIUI_APP_SPEC", APP_SPEC)
    module_name, _, attr = spec.partition(":")
    mod = importlib.import_module(module_name)
    miki_app = getattr(mod, attr or "app")
    return CREATE_APP(miki_app)
