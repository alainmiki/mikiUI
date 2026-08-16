"""Input validation system for MikiUI.

Provides a composable validator API with clear error messages.
"""

from __future__ import annotations

import re
from typing import Any


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, errors: dict[str, str]) -> None:
        self.errors = errors
        super().__init__(str(errors))


class Validator:
    """Base class for all validators.

    Subclasses must implement :meth:`validate`.
    """

    def validate(self, value: Any) -> str | None:
        """Validate ``value`` and return an error message, or ``None`` if valid."""
        raise NotImplementedError


class Required(Validator):
    """Validator that checks a field is present and non-empty."""

    def validate(self, value: Any) -> str | None:
        if value is None:
            return "Field is required"
        if isinstance(value, str) and not value.strip():
            return "Field is required"
        return None


class Length(Validator):
    """Validator that checks a string's length is within bounds.

    Parameters
    ----------
    min:
        Minimum allowed length (inclusive).
    max:
        Maximum allowed length (inclusive).
    """

    def __init__(self, min: int = 0, max: int | None = None) -> None:
        self.min = min
        self.max = max

    def validate(self, value: Any) -> str | None:
        if value is None:
            return None
        length = len(str(value))
        if length < self.min:
            return f"Must be at least {self.min} characters"
        if self.max is not None and length > self.max:
            return f"Must be at most {self.max} characters"
        return None


class Range(Validator):
    """Validator that checks a numeric value is within bounds.

    Parameters
    ----------
    min:
        Minimum allowed value (inclusive).
    max:
        Maximum allowed value (inclusive).
    """

    def __init__(self, min: float | None = None, max: float | None = None) -> None:
        self.min = min
        self.max = max

    def validate(self, value: Any) -> str | None:
        if value is None:
            return None
        try:
            num = float(value)
        except (TypeError, ValueError):
            return "Must be a number"
        if self.min is not None and num < self.min:
            return f"Must be >= {self.min}"
        if self.max is not None and num > self.max:
            return f"Must be <= {self.max}"
        return None


class Pattern(Validator):
    """Validator that checks a value matches a regular expression.

    Parameters
    ----------
    regex:
        Regular expression pattern to match.
    """

    def __init__(self, regex: str) -> None:
        self._pattern = re.compile(regex)

    def validate(self, value: Any) -> str | None:
        if value is None:
            return None
        if not self._pattern.search(str(value)):
            return f"Does not match required pattern: {self._pattern.pattern}"
        return None


class Email(Validator):
    """Validator that checks a value is a valid email address."""

    _PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def validate(self, value: Any) -> str | None:
        if value is None:
            return None
        if not self._PATTERN.match(str(value)):
            return "Invalid email address"
        return None


class URL(Validator):
    """Validator that checks a value is a valid URL."""

    _PATTERN = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    def validate(self, value: Any) -> str | None:
        if value is None:
            return None
        if not self._PATTERN.match(str(value)):
            return "Invalid URL"
        return None


class DateTime(Validator):
    """Validator that parses a value as an ISO-8601 datetime string."""

    _FORMATS = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    def validate(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        for fmt in self._FORMATS:
            try:
                import datetime
                datetime.datetime.strptime(text, fmt)
                return None
            except ValueError:
                continue
        return "Invalid date/time format"


class Choice(Validator):
    """Validator that checks a value is within an allowed set.

    Parameters
    ----------
    choices:
        Iterable of allowed values.
    """

    def __init__(self, choices: list[Any]) -> None:
        self._choices = list(choices)

    def validate(self, value: Any) -> str | None:
        if value is None:
            return None
        if value not in self._choices:
            return f"Must be one of: {', '.join(str(c) for c in self._choices)}"
        return None


class Nested(Validator):
    """Validator that applies another validator to each value in a dict.

    Parameters
    ----------
    validator:
        Validator instance to apply to every value.
    """

    def __init__(self, validator: Validator) -> None:
        self._validator = validator

    def validate(self, value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            return "Must be a dictionary"
        for key, val in value.items():
            error = self._validator.validate(val)
            if error:
                return f"{key}: {error}"
        return None


def validate(
    data: dict[str, Any],
    schema: dict[str, Validator | list[Validator]],
) -> dict[str, str]:
    """Validate ``data`` against ``schema`` and return an errors dict.

    Parameters
    ----------
    data:
        Raw input values.
    schema:
        Mapping of field name to a :class:`Validator` instance or a list of
        validator instances (applied in order; stops on first error).

    Returns
    -------
    dict[str, str]
        Mapping of field name to error message. Empty dict means all valid.
    """
    errors: dict[str, str] = {}
    for field, validators in schema.items():
        value = data.get(field)
        validator_list = validators if isinstance(validators, list) else [validators]
        for validator in validator_list:
            error = validator.validate(value)
            if error:
                errors[field] = error
                break
    return errors
