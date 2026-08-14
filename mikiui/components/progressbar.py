"""Progress and meter components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Progress(Component):
    tag = "progress"


class Meter(Component):
    tag = "meter"


class Output(Component):
    tag = "output"
