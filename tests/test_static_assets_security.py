"""Tests for static asset path resolution security."""

from __future__ import annotations

import tempfile

from mikiui.app.static_assets import resolve_static_path


def test_resolve_static_path_within_mount():
    with tempfile.TemporaryDirectory() as tmp:
        from mikiui.app.static_assets import _ASSET_MOUNTS
        key = "/_test_static"
        _ASSET_MOUNTS[key] = tmp
        try:
            result = resolve_static_path(f"{key}/css/app.css")
            assert result is not None
            assert result.startswith(tmp)
        finally:
            _ASSET_MOUNTS.pop(key, None)


def test_resolve_static_path_rejects_traversal():
    with tempfile.TemporaryDirectory() as tmp:
        from mikiui.app.static_assets import _ASSET_MOUNTS
        key = "/_test_static"
        _ASSET_MOUNTS[key] = tmp
        try:
            result = resolve_static_path(f"{key}/../etc/passwd")
            assert result is None
        finally:
            _ASSET_MOUNTS.pop(key, None)


def test_resolve_static_path_no_match():
    result = resolve_static_path("/_nonexistent/file.txt")
    assert result is None
