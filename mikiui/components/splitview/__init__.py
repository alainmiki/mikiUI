"""VS Code-like SplitView editor area component package.

A recursive grid-based editor area with multiple resizable groups, each
containing a tab bar and content panels. Supports drag-and-drop between
groups, splitters, and keyboard navigation.

This package contains:
- splitview.py : EditorTab, EditorGroup, and SplitView components
- splitview.css: Scoped styles for the editor area
- splitview.js : Client-side behavior (tabs, drag-drop, splitters)
"""

from __future__ import annotations

from .splitview import EditorGroup, EditorTab, SplitView

__all__ = ["EditorGroup", "EditorTab", "SplitView"]
