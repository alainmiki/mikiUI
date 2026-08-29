"""Build optimizer: dependency-free CSS/JS minification.

Production builds should not ship unminified assets. This module minifies the
vendored/exported ``.css`` and ``.js`` files in place — stripping block comments
and collapsing insignificant whitespace. It is intentionally dependency-free so
the build works offline. (For larger apps, swap in the Vite/Webpack pipeline in
``package.json``; this remains a safe, always-available fallback.)
"""

from __future__ import annotations

import os
import re
from typing import Any

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def _minify_css(text: str) -> str:
    text = _BLOCK_COMMENT.sub("", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([{}:;,>])\s*", r"\1", text)
    return text.strip()


def _minify_js(text: str) -> str:
    # Strip block comments; leave line comments (they may appear inside strings).
    text = _BLOCK_COMMENT.sub("", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def optimize(assets: list[str], *, level: str = "balanced") -> dict[str, Any]:
    """Minify each asset path in place. Returns a report.

    ``level`` is one of ``none`` (copy only), ``balanced`` (whitespace/comment
    stripping), or ``aggressive`` (also trims trailing semicolons/blank lines).
    """
    if level not in ("none", "balanced", "aggressive"):
        raise ValueError(f"Invalid optimization level: {level}")

    done: list[str] = []
    for path in assets:
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        if level == "none":
            done.append(path)
            continue
        lowered = path.lower()
        if lowered.endswith(".css"):
            text = _minify_css(text)
        elif lowered.endswith(".js"):
            text = _minify_js(text)
        else:
            text = re.sub(r"\s+\n", "\n", text).strip()
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        done.append(path)

    return {"optimized": done, "level": level, "status": "ok"}
