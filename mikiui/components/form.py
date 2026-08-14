"""Form components."""

from __future__ import annotations

from typing import Any

from .base import Component


class Form(Component):
    tag = "form"


class Label(Component):
    tag = "label"


class Select(Component):
    tag = "select"


class Option(Component):
    tag = "option"


class Optgroup(Component):
    tag = "optgroup"


class Fieldset(Component):
    tag = "fieldset"


class Legend(Component):
    tag = "legend"
