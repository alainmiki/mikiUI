"""MediaPlayer widget: a video/audio player with an optional EQ caption."""

from __future__ import annotations

from typing import Any

from ..components import Audio, Div, Video
from ..components.base import Component
from ..engine import _


class MediaPlayer(Component):
    """Render a media player for a single ``source`` URL.

    :param source: URL of the media file.
    :param kind: ``"video"`` or ``"audio"``.
    :param eq: optional EQ preset name shown as a caption.
    :param controls: whether native playback controls are shown.
    """

    tag = "div"

    def __init__(
        self,
        source: str,
        kind: str = "video",
        eq: str | None = None,
        controls: bool = True,
        **attrs: Any,
    ) -> None:
        attrs.setdefault("class_", "miki-mediaplayer")
        attrs.setdefault("role", "region")
        attrs.setdefault("touch-action", "manipulation")
        label = _("mediaplayer_label", "Media player")
        if kind == "audio":
            media = Audio(src=source, controls=controls, aria_label=label)
        else:
            media = Video(src=source, controls=controls, aria_label=label)

        children: list[Any] = [media]
        if eq:
            children.append(
                Div(_("eq_preset", f"EQ: {eq}"), class_="miki-mediaplayer-eq")
            )
        super().__init__(*children, **attrs)
