"""Picture component: responsive image with multiple sources."""

from __future__ import annotations

from typing import Any

from .base import Component
from .html import Img


class Picture(Component):
    """Responsive ``<picture>`` wrapping an ``<img>`` and optional ``<source>``s.

    ``img_src`` sets the fallback ``<img src>``; ``alt`` its alt text. Any
    ``<source>`` children passed positionally are rendered before the image.
    """

    tag = "picture"

    def __init__(
        self,
        img_src: str,
        alt: str = "",
        *children: Any,
        **attrs: Any,
    ) -> None:
        img = Img(src=img_src, alt=alt)
        super().__init__(*children, img, **attrs)
