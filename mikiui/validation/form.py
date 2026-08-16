"""Form validation helpers for MikiUI.

Integrates with FastAPI request forms and provides HTMX-friendly error
responses.
"""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse

from ..engine.dom import Element, Text
from . import Validator, validate


class Field:
    """A single form field with a chain of validators.

    Parameters
    ----------
    name:
        The field name (matches the HTML ``name`` attribute).
    validators:
        One or more validators applied in order (stops on first error).
    """

    def __init__(self, name: str, *validators: Validator) -> None:
        self.name = name
        self.validators = list(validators)

    def validate_value(self, value: Any) -> str | None:
        """Run validators against ``value`` and return the first error, or ``None``."""
        for validator in self.validators:
            error = validator.validate(value)
            if error:
                return error
        return None


class FormValidator:
    """Validates data from an HTML form submission.

    Parameters
    ----------
    fields:
        Sequence of :class:`Field` instances defining the expected schema.
    """

    def __init__(self, *fields: Field) -> None:
        self.fields = list(fields)
        self._schema: dict[str, list[Validator]] = {f.name: f.validators for f in fields}

    def validate(self, data: dict[str, Any]) -> dict[str, str]:
        """Validate ``data`` and return a field-name to error-message mapping."""
        return validate(data, self._schema)  # type: ignore[arg-type]

    async def validate_request(self, request: Request) -> tuple[dict[str, Any], dict[str, str]]:
        """Parse a FastAPI request and validate its form body.

        Returns
        -------
        tuple[dict[str, Any], dict[str, str]]
            ``(raw_data, errors)`` where ``errors`` is empty when valid.
        """
        try:
            form = await request.form()
            data = dict(form)
        except Exception:
            data = {}
        errors = self.validate(data)
        return data, errors


class Form:
    """Collects fields and validates form data.

    Parameters
    ----------
    validator:
        A :class:`FormValidator` instance.
    """

    def __init__(self, validator: FormValidator) -> None:
        self.validator = validator

    def validate(self, data: dict[str, Any]) -> dict[str, str]:
        """Validate ``data`` against the form's schema."""
        return self.validator.validate(data)

    async def validate_request(self, request: Request) -> tuple[dict[str, Any], dict[str, str]]:
        """Parse and validate an incoming FastAPI request."""
        return await self.validator.validate_request(request)


def htmx_error_response(errors: dict[str, str], *, status_code: int = 422) -> HTMLResponse:
    """Build an HTMX-friendly partial HTML response with validation errors.

    Parameters
    ----------
    errors:
        Mapping of field name to error message.
    status_code:
        HTTP status code (default ``422``).

    Returns
    -------
    HTMLResponse
        A response containing an error summary block.
    """
    if not errors:
        return HTMLResponse("", status_code=status_code)

    items = []
    for field, message in errors.items():
        items.append(
            Element(
                Text(f"{field}: {message}"),
                class_="miki-field-error",
            ).to_html()
        )
    body = Element(
        Element("Invalid submission", tag="h4", class_="miki-error-title"),
        Element("".join(items), tag="div", class_="miki-error-list"),
        tag="div",
        class_="miki-validation-errors",
        role="alert",
    ).to_html()
    return HTMLResponse(body, status_code=status_code, headers={"HX-Retarget": ".miki-validation-errors"})


__all__ = ["Field", "FormValidator", "Form", "htmx_error_response"]
