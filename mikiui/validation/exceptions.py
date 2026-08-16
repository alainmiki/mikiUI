"""Validation-related exceptions."""

from __future__ import annotations


class ValidationError(Exception):
    """Raised when form or input validation fails."""

    def __init__(self, errors: dict[str, str]) -> None:
        self.errors = errors
        super().__init__(str(errors))
