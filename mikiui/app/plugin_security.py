"""Plugin security, manifest schema, and sandboxing for MikiUI.

Provides:

1. **Plugin manifest** — a structured schema a plugin ships with so the
   framework (and a future marketplace) can validate identity, capabilities,
   and compatibility before the plugin is ever loaded.
2. **Security policy** — a configurable allow/deny list for imports,
   filesystem access, and network use.
3. **AST vetter** — static analysis of plugin source code to detect dangerous
   patterns (``subprocess``, ``eval``/``exec``, raw file deletion, etc.)
   before the module is executed.
4. **Plugin validator** — runs manifest checks, AST vetting, and import
   scanning against a :class:`PluginSecurityConfig`.

Security is enforced in two places:

* **Discovery time** — :func:`mikiui.app.plugin_discovery.discover_plugins`
  can optionally reject plugins whose manifest or source violates policy.
* **Registration time** — :meth:`MikiApp.use` calls the validator before
  ``plugin.register(self)`` so even manually instantiated plugins are checked.

A plugin that fails validation raises :class:`PluginSecurityViolation`
and is **not registered**.
"""

from __future__ import annotations

import ast
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from ..app.plugins import Plugin

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Manifest schema
# ---------------------------------------------------------------------------

@dataclass
class PluginManifest:
    """Structured metadata for a MikiUI plugin.

    A plugin may expose its manifest as a module-level ``PLUGIN_MANIFEST``
    dict or as a ``plugin.json`` file next to the module.  When neither is
    present the validator falls back to module attributes (``__name__``,
    ``__version__``, ``__doc__``).

    Attributes:
        name: Unique plugin identifier (must match ``plugin.name``).
        version: Semver string.
        description: Human-readable description.
        author: Maintainer name or org.
        license: SPDX license identifier.
        min_mikiui_version: Minimum MikiUI version required.
        dependencies: Plugin names this plugin requires.
        capabilities: Declared capabilities (e.g. ``["filesystem:read"]``).
        homepage: Optional project URL.
        repository: Optional source repository URL.
        source: Where the plugin came from (``"builtin"``, ``"local"``,
            ``"entry_point"``, ``"marketplace"``).
        checksum: Optional SHA-256 of the plugin package for integrity
            verification.
    """

    name: str
    version: str
    description: str
    author: str
    license: str
    min_mikiui_version: str = "0.1.0"
    dependencies: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    homepage: str | None = None
    repository: str | None = None
    source: str = "unknown"
    checksum: str | None = None


# ---------------------------------------------------------------------------
# Security policy
# ---------------------------------------------------------------------------

@dataclass
class PluginSecurityConfig:
    """Configurable security policy for plugin loading.

    Attributes:
        allow_untrusted: If ``False``, only plugins whose ``source`` is
            ``"builtin"`` or ``"entry_point"`` may be loaded.  Local-dir
            and marketplace plugins are blocked unless explicitly trusted.
        allowed_imports: Import allow-list.  When non-empty, only these
            top-level module names may be imported by the plugin.  Empty
            list means the default safe list is used (stdlib + mikiui +
            common data science libs).
        blocked_imports: Explicit deny-list.  These imports always raise
            :class:`PluginSecurityViolation` regardless of the allow-list.
        blocked_capabilities: Capabilities that may not be granted to any
            plugin.  Use this to disable ``filesystem:write`` or
            ``network:outbound`` globally.
        allow_filesystem_write: Global toggle for write access outside the
            app's working directory.
        allow_network: Global toggle for outbound network access.
        vet_ast: If ``True``, scan plugin source for dangerous AST patterns
            before execution.
        max_plugin_size_bytes: Reject plugins larger than this (0 = no limit).
    """

    allow_untrusted: bool = False
    allowed_imports: list[str] = field(default_factory=list)
    blocked_imports: list[str] = field(
        default_factory=lambda: [
            "subprocess",
            "os.system",
            "os.popen",
            "shutil.rmtree",
            "eval",
            "exec",
            "__import__",
            "importlib.import_module",
        ]
    )
    blocked_capabilities: list[str] = field(default_factory=list)
    allow_filesystem_write: bool = False
    allow_network: bool = True
    vet_ast: bool = True
    max_plugin_size_bytes: int = 0


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class PluginSecurityViolation(Exception):
    """Raised when a plugin violates the security policy."""


# ---------------------------------------------------------------------------
# AST vetter
# ---------------------------------------------------------------------------

# Dangerous call patterns: (func_name, allowed_containing_types)
# We flag these when they appear as direct calls or attribute calls.
_DANGEROUS_CALLS: dict[str, tuple[str, ...]] = {
    "subprocess.run": ("subprocess",),
    "subprocess.Popen": ("subprocess",),
    "subprocess.call": ("subprocess",),
    "subprocess.check_output": ("subprocess",),
    "os.system": ("os",),
    "os.popen": ("os",),
    "os.spawn": ("os",),
    "os.exec": ("os",),
    "shutil.rmtree": ("shutil",),
    "eval": ("builtins",),
    "exec": ("builtins",),
    "compile": ("builtins",),
    "__import__": ("builtins",),
    "importlib.import_module": ("importlib",),
    "socket.socket": ("socket",),
    "requests.post": ("requests",),
    "requests.get": ("requests",),
    "aiohttp.ClientSession": ("aiohttp",),
}

# Dangerous attribute assignments (e.g. __builtins__ manipulation)
_DANGEROUS_ATTR_ASSIGNMENTS = {"__builtins__", "__globals__", "__code__"}


def _check_ast(tree: ast.AST) -> list[str]:
    """Walk *tree* and return a list of security violation descriptions."""
    violations: list[str] = []

    for node in ast.walk(tree):
        # Block dangerous calls.
        if isinstance(node, ast.Call):
            func = node.func
            name = ""
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                parts: list[str] = []
                cur: ast.expr | None = func
                while isinstance(cur, ast.Attribute):
                    parts.insert(0, cur.attr)
                    cur = cur.value
                if isinstance(cur, ast.Name):
                    parts.insert(0, cur.id)
                name = ".".join(parts)

            if name in _DANGEROUS_CALLS:
                allowed_types = _DANGEROUS_CALLS[name]
                # Allow if the call is inside an allowed containing type.
                parent_name = _get_enclosing_name(tree, node)
                if parent_name not in allowed_types:
                    violations.append(
                        f"Dangerous call to {name!r} at line {node.lineno}"
                    )

        # Block dangerous attribute assignments.
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    if target.attr in _DANGEROUS_ATTR_ASSIGNMENTS:
                        violations.append(
                            f"Dangerous attribute assignment to {target.attr!r} at line {node.lineno}"
                        )

    return violations


def _get_enclosing_name(tree: ast.AST, target: ast.AST) -> str | None:
    """Return the name of the nearest enclosing class/function, or None."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if any(
                _is_descendant(child, target) or child is target
                for child in ast.iter_child_nodes(node)
            ):
                return node.name
    return None


def _is_descendant(parent: ast.AST, child: ast.AST) -> bool:
    """Return True if *child* is somewhere inside *parent*."""
    for node in ast.walk(parent):
        if node is child:
            return True
    return False


# ---------------------------------------------------------------------------
# Import scanner
# ---------------------------------------------------------------------------

def _extract_imports(tree: ast.AST, *, module: str | None = None) -> set[str]:
    """Return the set of top-level module names imported by *tree*.

    Relative imports (``from .sibling import x``) are resolved against *module*
    so they are checked as their full package path (e.g. ``mikiui_app_plugins``).
    """
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                imports.add(top)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if node.level > 0 and module:
                    parts = module.split(".")
                    pkg_parts = parts[: len(parts) - node.level + 1]
                    resolved = ".".join(pkg_parts)
                    if node.module:
                        resolved = f"{resolved}.{node.module}"
                    top = resolved.split(".")[0]
                    imports.add(top)
                else:
                    top = node.module.split(".")[0]
                    imports.add(top)
    return imports


# ---------------------------------------------------------------------------
# Default safe import list
# ---------------------------------------------------------------------------

_DEFAULT_SAFE_IMPORTS: set[str] = {
    "__future__",
    "abc",
    "argparse",
    "asyncio",
    "base64",
    "bisect",
    "calendar",
    "collections",
    "copy",
    "csv",
    "dataclasses",
    "datetime",
    "enum",
    "fnmatch",
    "functools",
    "glob",
    "hashlib",
    "heapq",
    "hmac",
    "html",
    "http",
    "inspect",
    "io",
    "itertools",
    "json",
    "logging",
    "math",
    "numbers",
    "operator",
    "os",
    "pathlib",
    "pprint",
    "random",
    "re",
    "secrets",
    "shutil",
    "signal",
    "socket",
    "sqlite3",
    "ssl",
    "statistics",
    "string",
    "struct",
    "subprocess",
    "tempfile",
    "textwrap",
    "threading",
    "time",
    "traceback",
    "types",
    "typing",
    "unicodedata",
    "urllib",
    "uuid",
    "warnings",
    "xml",
    "zipfile",
    "zoneinfo",
    "mikiui",
    "mikiui_app_plugins",
    "session",
    "notifications",
    "api",
    "demo",
    "fastapi",
    "starlette",
    "pydantic",
    "uvicorn",
    "aiofiles",
    "jinja2",
    "yaml",
    "toml",
    "dotenv",
}


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

class PluginValidator:
    """Validates a plugin against the security policy before registration.

    Usage::

        from mikiui.app.plugin_security import PluginValidator, PluginSecurityConfig

        config = PluginSecurityConfig(allow_untrusted=False, vet_ast=True)
        validator = PluginValidator(config)

        validator.validate_plugin(my_plugin)
    """

    def __init__(self, config: PluginSecurityConfig | None = None) -> None:
        self.config = config or PluginSecurityConfig()

    def validate_plugin(
        self,
        plugin: Plugin,
        manifest: PluginManifest | None = None,
        source_code: str | None = None,
    ) -> None:
        """Run all security checks against *plugin*.

        Parameters
        ----------
        plugin:
            The plugin instance to validate.
        manifest:
            Optional manifest.  If omitted, the validator falls back to
            ``plugin.PLUGIN_MANIFEST`` or module-level attributes.
        source_code:
            Optional raw source string for AST vetting.  If omitted and
            ``vet_ast`` is enabled, the validator attempts to read the
            plugin class's ``__module__`` file.

        Raises
        ------
        PluginSecurityViolation
            If any check fails.
        """
        self._validate_identity(plugin, manifest)
        self._validate_capabilities(plugin, manifest)
        if self.config.vet_ast:
            self._vet_plugin_ast(plugin, source_code)
        self._validate_imports(plugin, source_code)

    # ------------------------------------------------------------------
    # Identity / manifest checks
    # ------------------------------------------------------------------

    def _validate_identity(
        self, plugin: Plugin, manifest: PluginManifest | None
    ) -> None:
        if not plugin.name or not plugin.name.strip():
            raise PluginSecurityViolation("Plugin must have a non-empty name.")
        if manifest is not None:
            if manifest.name != plugin.name:
                raise PluginSecurityViolation(
                    f"Plugin name {plugin.name!r} does not match manifest name {manifest.name!r}."
                )

    def _validate_capabilities(
        self, plugin: Plugin, manifest: PluginManifest | None
    ) -> None:
        capabilities: list[str] = getattr(plugin, "capabilities", [])
        if manifest is not None and manifest.capabilities:
            capabilities = list(set(capabilities) | set(manifest.capabilities))
        for cap in capabilities:
            if cap in self.config.blocked_capabilities:
                raise PluginSecurityViolation(
                    f"Plugin {plugin.name!r} declares blocked capability {cap!r}."
                )

    # ------------------------------------------------------------------
    # AST vetting
    # ------------------------------------------------------------------

    def _vet_plugin_ast(self, plugin: Plugin, source_code: str | None) -> None:
        if source_code is None:
            source_code = self._resolve_source(plugin)
        if not source_code:
            return
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            raise PluginSecurityViolation(
                f"Plugin {plugin.name!r} source could not be parsed."
            )
        violations = _check_ast(tree)
        if violations:
            msgs = "; ".join(violations)
            raise PluginSecurityViolation(
                f"Plugin {plugin.name!r} failed AST security check: {msgs}"
            )

    def _resolve_source(self, plugin: Plugin) -> str | None:
        module = getattr(plugin, "__module__", None)
        if not module:
            return None
        # Map module name to file path.
        module_path = module.replace(".", os.sep) + ".py"
        candidates = [
            module_path,
            os.path.join("mikiui_app_plugins", module_path),
        ]
        for candidate in candidates:
            if os.path.isfile(candidate):
                try:
                    with open(candidate, encoding="utf-8") as fh:
                        return fh.read()
                except OSError:
                    continue
        return None

    # ------------------------------------------------------------------
    # Import scanning
    # ------------------------------------------------------------------

    def _validate_imports(self, plugin: Plugin, source_code: str | None) -> None:
        if source_code is None:
            source_code = self._resolve_source(plugin)
        if not source_code:
            return
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return
        imports = _extract_imports(tree, module=getattr(plugin, "__module__", None))
        blocked = imports & set(self.config.blocked_imports)
        if blocked:
            raise PluginSecurityViolation(
                f"Plugin {plugin.name!r} imports blocked modules: {sorted(blocked)}"
            )
        allowed = set(self.config.allowed_imports) or _DEFAULT_SAFE_IMPORTS
        # Allow mikiui internals regardless.
        allowed = allowed | {"mikiui", "mikiui_app_plugins"}
        disallowed = imports - allowed
        if disallowed:
            raise PluginSecurityViolation(
                f"Plugin {plugin.name!r} imports non-allowlisted modules: "
                f"{sorted(disallowed)}. Allowed: {sorted(allowed)}"
            )


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def validate_plugin(
    plugin: Plugin,
    config: PluginSecurityConfig | None = None,
    manifest: PluginManifest | None = None,
    source_code: str | None = None,
) -> None:
    """Validate *plugin* against the default security policy.

    Raises
    ------
    PluginSecurityViolation
        If the plugin fails any security check.
    """
    validator = PluginValidator(config)
    validator.validate_plugin(plugin, manifest=manifest, source_code=source_code)


def load_manifest(module: Any) -> PluginManifest | None:
    """Try to load a :class:`PluginManifest` from a plugin module.

    Checks (in order):
    1. ``module.PLUGIN_MANIFEST`` dict.
    2. ``plugin.json`` next to the module file.
    3. Module attributes (``__name__``, ``__version__``, ``__doc__``).

    Returns ``None`` if no manifest is found.
    """
    # 1. Module-level dict.
    raw = getattr(module, "PLUGIN_MANIFEST", None)
    if isinstance(raw, dict):
        try:
            return PluginManifest(**raw)
        except TypeError:
            pass

    # 2. plugin.json next to the module file.
    module_file = getattr(module, "__file__", None)
    if module_file:
        candidate = os.path.join(os.path.dirname(module_file), "plugin.json")
        if os.path.isfile(candidate):
            try:
                import json

                with open(candidate, encoding="utf-8") as fh:
                    raw = json.load(fh)
                return PluginManifest(**raw)
            except Exception:
                pass

    # 3. Module attributes.
    name = getattr(module, "__name__", "").split(".")[-1]
    version = getattr(module, "__version__", "0.0.0")
    doc = (getattr(module, "__doc__", "") or "").strip().split("\n")[0]
    if name:
        return PluginManifest(
            name=name,
            version=version,
            description=doc or "No description.",
            author="unknown",
            license="MIT",
            source="unknown",
        )
    return None


__all__ = [
    "PluginManifest",
    "PluginSecurityConfig",
    "PluginSecurityViolation",
    "PluginValidator",
    "validate_plugin",
    "load_manifest",
]
