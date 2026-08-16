"""MikiUI media package.

Provides streaming, recording, equalizer, and audio filter utilities for the
MikiUI framework. All modules are pure-Python and dependency-free.
"""

from .equalizer import Equalizer
from .filters import Filters
from .recorder import Recorder
from .streaming import StreamingManager, sse_chunk

__all__ = [
    "StreamingManager",
    "sse_chunk",
    "Recorder",
    "Equalizer",
    "Filters",
]
