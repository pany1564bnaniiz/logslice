"""Tests for logslice.normalizer."""

from __future__ import annotations

import pytest

from logslice.normalizer import (
    NormalizerError,
    apply_normalizations,
    lowercase_field,
    normalize_field,
    strip_field,
    uppercase_field,
)


# ---------------------------------------------------------------------------
# normalize_field
# ---------------------------------------------------------------------------

def test_normalize_field_applies_transform():
    record = {"level": "INFO"}
    result = normalize_field(record, "level", str.lower)
    assert result["level"] == "info"


def test_normalize_field_does_not_mutate_original():
    record = {"level": "INFO"}
    normalize_field(record, "level", str.lower)
    assert record["level"] == "INFO"


def test_normalize_field_missing_key_leaves_record_unchanged():
    record = {"msg": "hello"}
    result = normalize_field(record, "level", str.lower)
    assert result == {"msg": "hello"}


def test_normalize_field_empty_field_raises():
    with pytest.raises(NormalizerError, match="field name must not be empty"):
        normalize_field({"a": 1}, "", str.lower)


def test_normalize_field_whitespace_field_raises():
    with pytest.raises(NormalizerError, match="field name must not be empty"):
        normalize_field({"a": 1}, "   ", str.lower)


def test_normalize_field_transform_exception_raises_normalizer_error():
    def _boom(v):
        raise ValueError("bad value")

    with pytest.raises(NormalizerError, match="transform failed"):
        normalize_field({"x": 1}, "x", _boom)


# ---------------------------------------------------------------------------
# lowercase_field
# ---------------------------------------------------------------------------

def test_lowercase_field_basic():
    assert lowercase_field({"level": "ERROR"}, "level") == {"level": "error"}


def test_lowercase_field_non_string_raises():
    with pytest.raises(NormalizerError):
        lowercase_field({"count": 42}, "count")


# ---------------------------------------------------------------------------
# uppercase_field
# ---------------------------------------------------------------------------

def test_uppercase_field_basic():
    assert uppercase_field({"level": "info"}, "level") == {"level": "INFO"}


def test_uppercase_field_non_string_raises():
    with pytest.raises(NormalizerError):
        uppercase_field({"count": 3}, "count")


# ---------------------------------------------------------------------------
# strip_field
# ---------------------------------------------------------------------------

def test_strip_field_removes_whitespace():
    assert strip_field({"msg": "  hello  "}, "msg") == {"msg": "hello"}


def test_strip_field_no_whitespace_unchanged():
    assert strip_field({"msg": "hello"}, "msg") == {"msg": "hello"}


def test_strip_field_non_string_raises():
    with pytest.raises(NormalizerError):
        strip_field({"n": 1}, "n")


# ---------------------------------------------------------------------------
# apply_normalizations
# ---------------------------------------------------------------------------

def test_apply_normalizations_lowercase_all_records():
    records = [{"level": "INFO"}, {"level": "ERROR"}]
    result = apply_normalizations(records, [{"type": "lowercase", "field": "level"}])
    assert [r["level"] for r in result] == ["info", "error"]


def test_apply_normalizations_multiple_specs():
    records = [{"level": "  Info  ", "env": "prod"}]
    specs = [
        {"type": "strip", "field": "level"},
        {"type": "uppercase", "field": "env"},
    ]
    result = apply_normalizations(records, specs)
    assert result[0]["level"] == "Info"
    assert result[0]["env"] == "PROD"


def test_apply_normalizations_custom_transform():
    records = [{"msg": "hello world"}]
    specs = [{"type": "custom", "field": "msg", "transform": lambda v: v.replace(" ", "_")}]
    result = apply_normalizations(records, specs)
    assert result[0]["msg"] == "hello_world"


def test_apply_normalizations_unknown_type_raises():
    with pytest.raises(NormalizerError, match="unknown normalization type"):
        apply_normalizations([{"a": 1}], [{"type": "explode", "field": "a"}])


def test_apply_normalizations_empty_records_returns_empty():
    result = apply_normalizations([], [{"type": "lowercase", "field": "level"}])
    assert result == []


def test_apply_normalizations_preserves_original_records():
    records = [{"level": "INFO"}]
    apply_normalizations(records, [{"type": "lowercase", "field": "level"}])
    assert records[0]["level"] == "INFO"
