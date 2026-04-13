"""Tests for logslice.validator."""

import pytest

from logslice.validator import (
    ValidatorError,
    apply_validations,
    require_field_type,
    require_fields,
)


# --- require_fields ---

def test_require_fields_all_present():
    assert require_fields({"level": "info", "msg": "hello"}, ["level", "msg"]) is True


def test_require_fields_missing_field():
    assert require_fields({"level": "info"}, ["level", "msg"]) is False


def test_require_fields_empty_value_excluded():
    assert require_fields({"level": ""}, ["level"]) is False


def test_require_fields_none_value_excluded():
    assert require_fields({"level": None}, ["level"]) is False


def test_require_fields_empty_list_raises():
    with pytest.raises(ValidatorError, match="must not be empty"):
        require_fields({"level": "info"}, [])


def test_require_fields_blank_field_name_raises():
    with pytest.raises(ValidatorError, match="must not be blank"):
        require_fields({"level": "info"}, ["  "])


# --- require_field_type ---

def test_require_field_type_correct_type():
    assert require_field_type({"count": 42}, "count", int) is True


def test_require_field_type_wrong_type():
    assert require_field_type({"count": "42"}, "count", int) is False


def test_require_field_type_missing_field():
    assert require_field_type({}, "count", int) is False


def test_require_field_type_blank_field_raises():
    with pytest.raises(ValidatorError, match="must not be blank"):
        require_field_type({"count": 1}, "", int)


def test_require_field_type_invalid_type_raises():
    with pytest.raises(ValidatorError, match="must be a Python type"):
        require_field_type({"count": 1}, "count", "int")  # type: ignore


# --- apply_validations ---

def test_apply_validations_no_filters_passes_all():
    records = [{"a": 1}, {"b": 2}]
    assert apply_validations(records) == records


def test_apply_validations_required_fields_filters():
    records = [
        {"level": "info", "msg": "ok"},
        {"level": "warn"},
        {"msg": "no level"},
    ]
    result = apply_validations(records, required_fields=["level", "msg"])
    assert result == [{"level": "info", "msg": "ok"}]


def test_apply_validations_field_type_filters():
    records = [
        {"ts": 1000, "msg": "a"},
        {"ts": "not-a-number", "msg": "b"},
        {"msg": "c"},
    ]
    result = apply_validations(records, field_type=("ts", int))
    assert result == [{"ts": 1000, "msg": "a"}]


def test_apply_validations_combined_filters():
    records = [
        {"level": "info", "count": 3},
        {"level": "warn", "count": "bad"},
        {"count": 5},
    ]
    result = apply_validations(
        records, required_fields=["level", "count"], field_type=("count", int)
    )
    assert result == [{"level": "info", "count": 3}]


def test_apply_validations_empty_records():
    assert apply_validations([], required_fields=["level"]) == []


def test_apply_validations_invalid_required_fields_raises():
    with pytest.raises(ValidatorError):
        apply_validations([{"a": 1}], required_fields=[])
