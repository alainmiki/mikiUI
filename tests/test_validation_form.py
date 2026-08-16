"""Tests for MikiUI form validation."""

from __future__ import annotations

import pytest

from mikiui.validation import Email, Length, Required
from mikiui.validation.form import Field, Form, FormValidator, htmx_error_response


class DummyRequest:
    """Minimal request stand-in for offline tests."""

    def __init__(self, form_data: dict[str, str]) -> None:
        self._form_data = form_data
        self.headers = {}
        self.url = type("U", (), {"path": "/test"})()

    async def form(self):
        return self._form_data


class TestField:
    def test_valid(self):
        f = Field("name", Required(), Length(min=2))
        assert f.validate_value("Alice") is None

    def test_invalid(self):
        f = Field("name", Required(), Length(min=2))
        assert f.validate_value("") == "Field is required"
        assert f.validate_value("A") == "Must be at least 2 characters"


class TestFormValidator:
    def test_valid(self):
        v = FormValidator(Field("email", Required(), Email()))
        data = {"email": "a@b.com"}
        assert v.validate(data) == {}

    def test_invalid(self):
        v = FormValidator(Field("email", Required(), Email()))
        data = {"email": "bad"}
        errors = v.validate(data)
        assert "email" in errors

    @pytest.mark.asyncio
    async def test_validate_request(self):
        v = FormValidator(Field("q", Required()))
        req = DummyRequest({"q": "hello"})
        data, errors = await v.validate_request(req)
        assert data == {"q": "hello"}
        assert errors == {}


class TestForm:
    def test_valid(self):
        v = FormValidator(Field("name", Required()))
        form = Form(v)
        errors = form.validate({"name": "x"})
        assert errors == {}

    def test_invalid(self):
        v = FormValidator(Field("name", Required()))
        form = Form(v)
        errors = form.validate({})
        assert "name" in errors


class TestHtmxErrorResponse:
    def test_empty_errors(self):
        resp = htmx_error_response({})
        assert resp.status_code == 422
        assert resp.body == b""

    def test_with_errors(self):
        resp = htmx_error_response({"name": "Required"})
        assert resp.status_code == 422
        assert b"miki-validation-errors" in resp.body
        assert b"name: Required" in resp.body
