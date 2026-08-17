"""Auto-discovery of the user's MikiApp.

When the user runs ``mikiui dev`` or ``mikiui desktop`` without ``--app``,
this module searches the current working directory for a file that defines a
:class:`~mikiui.app.MikiApp` instance.  It looks for, in order:

1. ``app.py``  — the convention over configuration choice.
2. ``main.py`` — a common alternative.
3. ``server.py`` — another common name.
4. Any ``*.py`` file in the root that contains a ``MikiApp(...)`` instance
   at module level (scanning the file's AST, without importing it).

The discovered module/attr is returned as a ``"module:attr"`` spec string so
the CLI can pass it to uvicorn (with reload) or use it directly.

If no MikiApp instance is found, an :class:`AppDiscoveryError` is raised with
a verbose message listing the search criteria and actionable suggestions.
"""

from __future__ import annotations

import ast
import importlib
import os
import sys
from typing import Any

#: Candidate filenames to check, in priority order.
CANDIDATE_FILES = ("app.py", "main.py", "server.py")

#: Attribute names that typically hold the MikiApp instance.
CANDIDATE_ATTRS = ("app", "application", "miki_app", "create_app")


class AppDiscoveryError(Exception):
    """Raised when no MikiApp instance can be found via auto-discovery."""


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
        # Direct instance stored on module
        if isinstance(obj, MikiApp):
            return f"{module_name}:{attr}"
        # Factory function that returns a MikiApp when called (create_app())
        if attr == "create_app" and callable(obj):
            try:
                maybe_app = obj()
            except Exception:
                maybe_app = None
            if isinstance(maybe_app, MikiApp):
                return f"{module_name}:{attr}()"

    # Scan module-level assignments for any MikiApp instance.
    for name, val in vars(mod).items():
        if isinstance(val, MikiApp) and not name.startswith("_"):
            return f"{module_name}:{name}"
        if name == "create_app" and callable(val):
            try:
                maybe_app = val()
            except Exception:
                maybe_app = None
            if isinstance(maybe_app, MikiApp):
                return f"{module_name}:{name}()"

    return None


def _scan_file_for_app(filepath: str) -> tuple[str, str] | None:
    """Scan a Python file's AST for a module-level MikiApp instance.

    This avoids importing the file, which can fail or have side effects.
    Returns ``(module_name, attr_name)`` or ``None``.
    """
    filename = os.path.basename(filepath)
    module_name = filename[:-3]  # strip .py

    try:
        with open(filepath, encoding="utf-8") as f:
            source = f.read()
    except OSError:
        return None

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return None

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            # Check: var = MikiApp(...)  or  var = MikiApp
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    if _is_miki_app_call(node.value) or _is_miki_app_name(node.value):
                        return (module_name, target.id)
        elif isinstance(node, ast.AnnAssign):
            # Check: var: MikiApp = MikiApp(...)
            target = node.target
            if isinstance(target, ast.Name) and not target.id.startswith("_"):
                if node.value and (_is_miki_app_call(node.value) or _is_miki_app_name(node.value)):
                    return (module_name, target.id)
        elif isinstance(node, ast.FunctionDef):
            # Check: def create_app(): return MikiApp(...)
            if node.name == "create_app" and _returns_miki_app(node):
                return (module_name, "create_app")

    return None


def _is_miki_app_call(node: ast.AST) -> bool:
    """Check if an AST node is a call to ``MikiApp(...)``."""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "MikiApp"
    )


def _is_miki_app_name(node: ast.AST) -> bool:
    """Check if an AST node is a bare reference to ``MikiApp``."""
    return isinstance(node, ast.Name) and node.id == "MikiApp"


def _returns_miki_app(func_node: ast.FunctionDef) -> bool:
    """Check if a function body contains a return of a MikiApp(...) call."""
    for child in ast.walk(func_node):
        if isinstance(child, ast.Return) and child.value:
            if _is_miki_app_call(child.value):
                return True
    return False


def discover_app() -> str | None:
    """Auto-discover the app spec (``"module:attr"``) in the current directory.

    Search order:
    1. Candidate files (``app.py``, ``main.py``, ``server.py``) — imported
       and inspected for common attribute names.
    2. All *.py files in CWD root — AST-scanned for ``MikiApp(...)`` usage
       without importing (safe for files with side effects).

    Returns ``None`` if no MikiApp instance is found.
    """
    cwd = os.getcwd()
    searched: list[str] = []

    # 1. Check candidate files in priority order (import + inspect).
    for module_name in _candidate_modules():
        searched.append(module_name)
        spec = _find_app_in_module(module_name)
        if spec:
            return spec

    # 2. AST-scan all .py files in the CWD root for MikiApp usage.
    for fname in sorted(os.listdir(cwd)):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        module_name = fname[:-3]
        if module_name in (fm for fm in _candidate_modules()):
            continue  # Already tried above via import
        searched.append(module_name)
        filepath = os.path.join(cwd, fname)
        result = _scan_file_for_app(filepath)
        if result:
            module_name, attr = result
            if attr == "create_app":
                return f"{module_name}:create_app()"
            return f"{module_name}:{attr}"

    return None


def _build_error_message(searched_files: list[str]) -> str:
    """Build a verbose error message for when no app is found."""
    cwd = os.getcwd()
    py_files = sorted(
        f for f in os.listdir(cwd) if f.endswith(".py") and not f.startswith("_")
    )

    msg = [
        "No MikiApp instance found in the current directory.",
        "",
        "Auto-discovery searched for a file containing a MikiApp instance.",
        f"Files checked: {', '.join(searched_files) if searched_files else '(none)'}",
        "",
        "To fix this, make sure your app file contains a MikiApp instance:",
        "",
        "  from mikiui import MikiApp",
        "  app = MikiApp(title='My App')",
        "",
        "  @app.route('/')",
        "  def home():",
        "      return 'Hello'",
        "",
        "Then run:  mikiui dev --app app:app",
        "",
        "Or, if your app is in a different file:",
        "  mikiui dev --app my_app.py:app",
        "",
        f"Python files in {cwd}: {', '.join(py_files) if py_files else '(no .py files found)'}",
    ]
    return "\n".join(msg)


def resolve_app_spec(spec: str | None = None) -> str:
    """Return a valid ``"module:attr"`` spec.

    If ``spec`` is provided, validate it by importing the module.  If
    ``spec`` is ``None``, attempt auto-discovery by scanning the current
    working directory for a file that defines a MikiApp instance.

    Raises
    ------
    AppDiscoveryError
        If no MikiApp instance is found via auto-discovery.
    ValueError
        If the provided spec cannot be imported.
    """
    if spec:
        module_name, _, attr = spec.partition(":")
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # pragma: no cover - user error
            raise ValueError(f"Cannot import '{spec}': {exc}") from exc
        if not attr:
            spec = f"{module_name}:app"
        return spec

    discovered = discover_app()
    if discovered:
        return discovered

    # Build a list of searched files for the error message
    cwd = os.getcwd()
    searched = []
    for module_name in _candidate_modules():
        searched.append(module_name)
    for fname in sorted(os.listdir(cwd)):
        if fname.endswith(".py") and not fname.startswith("_"):
            module_name = fname[:-3]
            if module_name not in searched:
                searched.append(module_name)

    raise AppDiscoveryError(_build_error_message(searched))


def load_app(spec: str) -> Any:
    """Import and return the MikiApp instance from a ``"module:attr"`` spec."""
    module_name, _, attr = spec.partition(":")
    mod = importlib.import_module(module_name)
    if not attr:
        return getattr(mod, "app")
    # Support factory spec like "module:create_app()" — call it and return result
    if attr.endswith("()"):
        func_name = attr[:-2]
        func = getattr(mod, func_name)
        return func()
    return getattr(mod, attr)


__all__ = ["discover_app", "resolve_app_spec", "load_app", "CANDIDATE_FILES", "AppDiscoveryError"]
