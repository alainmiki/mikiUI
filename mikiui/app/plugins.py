"""Plugin base class.

Plugins are registered via ``app.use(plugin)``. A plugin may implement
``register(app)`` to hook into routing/rendering and ``on_render(tree)`` to
post-process the rendered output. Security-first: plugins run inside the app
process, so only trusted, validated plugins should be installed.
"""

from __future__ import annotations

from typing import Any


class Plugin:
    """Base class for MikiUI plugins.

    Override ``register`` to add routes/handlers and ``on_render`` to modify
    output before it is sent to the client.
    """

    name: str = "plugin"

    def register(self, app: Any) -> None:
        """Called by ``app.use``. Override to extend the app."""

    def on_render(self, tree: Any) -> Any:
        """Optional post-processing of a route's returned component tree."""
        return tree
