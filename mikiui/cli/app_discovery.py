"""Auto-discovery of the user's MikiApp.

When the user runs ``mikiui dev`` or ``mikiui desktop`` without ``--app``,
this module searches the current working directory for a file that defines a
:class:`~mikiui.app.MikiApp` instance.  It looks for, in order:

1. ``app.py``  — the convention over configuration choice.
2. ``main.py`` — a common alternative.
3. ``server.py`` — another common name.
4. Any ``*.py`` file in the root that contains an ``app = MikiApp(...)``
   assignment at import time.

The discovered module/attr is returned as a ``"module:attr"`` spec string so
the CLI can pass it to uvicorn (with reload) or use it directly.
"""

from __future__ import annotations

import importlib
import inspect
import os
import sys
from typing import Any

#: Candidate filenames to check, in priority order.
CANDIDATE_FILES = ("app.py", "main.py", "server.py")

#: Attribute names that typically hold the MikiApp instance.
CANDIDATE_ATTRS = ("app", "application", "miki_app")


def _candidate_modules() -> list[str]:
    """Return candidate module names based on files in the CWD."""
    result: list[str] = []
    cwd = os.getcwd()
    for fname in CANDIDATE_FILES:
        if os.path.isfile(os.path.join(cwd, fname)):
            result.append(fname[:-3])  # strip .py
    return result


def _find_app_in_module(module_name: str) -> str | None:
    """Try to import ``module_name`` and find a MikiApp instance attribute.

    Returns ``"module_name:attr"`` or ``None``.
    """
    from ..app import MikiApp

    if module_name in sys.modules:
        mod = sys.modules[module_name]
    else:
        try:
            mod = importlib.import_module(module_name)
        except Exception:
            return None

    for attr in CANDIDATE_ATTRS:
        obj = getattr(mod, attr, None)
        if isinstance(obj, MikiApp):
            return f"{module_name}:{attr}"

    # Scan module-level assignments for any MikiApp instance.
    for name, val in vars(mod).items():
        if isinstance(val, MikiApp) and not name.startswith("_"):
            return f"{module_name}:{name}"

    return None


def discover_app() -> str | None:
    """Auto-discover the app spec (``"module:attr"``) in the current directory.

    Returns ``None`` if no MikiApp instance is found.
    """
    # 1. Check candidate files in priority order.
    for module_name in _candidate_modules():
        spec = _find_app_in_module(module_name)
        if spec:
            return spec

    # 2. Scan all .py files in the CWD root for a MikiApp instance.
    from ..app import MikiApp

    cwd = os.getcwd()
    for fname in sorted(os.listdir(cwd)):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        module_name = fname[:-3]
        try:
            spec = _find_app_in_module(module_name)
        except Exception:
            continue
        if spec:
            return spec

    return None


def resolve_app_spec(spec: str | None = None) -> str:
    """Return a valid ``"module:attr"`` spec.

    If ``spec`` is provided, validate it.  If ``spec`` is ``None``, attempt
    auto-discovery.  Falls back to the demo app if nothing is found.
    """
    if spec:
        module_name, _, attr = spec.partition(":")
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - user error
            raise ValueError(f"Cannot import '{spec}': {exc}")
        if not attr:
            spec = f"{module_name}:app"
        return spec

    discovered = discover_app()
    if discovered:
        return discovered

    return "mikiui.examples.demo:app"


def load_app(spec: str) -> Any:
    """Import and return the MikiApp instance from a ``"module:attr"`` spec."""
    module_name, _, attr = spec.partition(":")
    mod = importlib.import_module(module_name)
    return getattr(mod, attr or "app")


__all__ = ["discover_app", "resolve_app_spec", "load_app", "CANDIDATE_FILES"]
