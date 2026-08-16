"""Tests for MikiUI input validation."""

from __future__ import annotations

from mikiui.validation import (
    URL,
    Choice,
    DateTime,
    Email,
    Length,
    Nested,
    Pattern,
    Range,
    Required,
    validate,
)
from mikiui.validation.exceptions import ValidationError


class TestRequired:
    def test_none_fails(self):
        assert Required().validate(None) == "Field is required"

    def test_empty_string_fails(self):
        assert Required().validate("") == "Field is required"
        assert Required().validate("   ") == "Field is required"

    def test_non_empty_passes(self):
        assert Required().validate("x") is None
        assert Required().validate(0) is None
        assert Required().validate(False) is None


class TestLength:
    def test_default_no_max(self):
        v = Length(min=2)
        assert v.validate("ab") is None
        assert v.validate("a") == "Must be at least 2 characters"

    def test_with_max(self):
        v = Length(min=2, max=4)
        assert v.validate("ab") is None
        assert v.validate("abcde") == "Must be at most 4 characters"

    def test_none_skips(self):
        assert Length(min=2).validate(None) is None


class TestRange:
    def test_in_range(self):
        v = Range(min=1, max=10)
        assert v.validate(5) is None
        assert v.validate("5") is None

    def test_out_of_range(self):
        v = Range(min=1, max=10)
        assert v.validate(0) == "Must be >= 1"
        assert v.validate(11) == "Must be <= 10"

    def test_non_numeric(self):
        assert Range().validate("abc") == "Must be a number"


class TestPattern:
    def test_match(self):
        v = Pattern(r"^\d+$")
        assert v.validate("123") is None

    def test_no_match(self):
        v = Pattern(r"^\d+$")
        assert "Does not match required pattern" in v.validate("abc")


class TestEmail:
    def test_valid(self):
        assert Email().validate("user@example.com") is None

    def test_invalid(self):
        assert Email().validate("bad") == "Invalid email address"


class TestURL:
    def test_valid_http(self):
        assert URL().validate("http://example.com") is None

    def test_valid_https(self):
        assert URL().validate("https://example.com/path") is None

    def test_invalid(self):
        assert URL().validate("not-a-url") == "Invalid URL"


class TestDateTime:
    def test_valid_iso(self):
        assert DateTime().validate("2024-01-01T12:00:00") is None

    def test_valid_date_only(self):
        assert DateTime().validate("2024-01-01") is None

    def test_invalid(self):
        assert DateTime().validate("not-a-date") == "Invalid date/time format"


class TestChoice:
    def test_valid_choice(self):
        v = Choice(["a", "b", "c"])
        assert v.validate("b") is None

    def test_invalid_choice(self):
        v = Choice(["a", "b", "c"])
        assert "Must be one of" in v.validate("d")


class TestNested:
    def test_valid_nested(self):
        v = Nested(Email())
        assert v.validate({"x": "a@b.com"}) is None

    def test_invalid_nested(self):
        v = Nested(Email())
        assert "x:" in v.validate({"x": "bad"})

    def test_not_dict(self):
        v = Nested(Email())
        assert v.validate("not-a-dict") == "Must be a dictionary"


class TestValidate:
    def test_valid_data(self):
        schema = {
            "name": Required(),
            "age": Range(min=0, max=150),
        }
        assert validate({"name": "Alice", "age": 30}, schema) == {}

    def test_invalid_data(self):
        schema = {
            "name": Required(),
            "age": Range(min=0, max=150),
        }
        errors = validate({"name": "", "age": 200}, schema)
        assert "name" in errors
        assert "age" in errors

    def test_list_validators(self):
        schema = {"email": [Required(), Email()]}
        errors = validate({"email": ""}, schema)
        assert errors["email"] == "Field is required"


class TestValidationError:
    def test_exception(self):
        err = ValidationError({"field": "bad"})
        assert err.errors == {"field": "bad"}
