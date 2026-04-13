"""Tests for logslice.truncator."""

import pytest

from logslice.truncator import (
    TruncatorError,
    apply_truncations,
    truncate_all_fields,
    truncate_field,
)


# ---------------------------------------------------------------------------
# truncate_field
# ---------------------------------------------------------------------------

def test_truncate_field_shortens_long_value():
    rec = {"msg": "hello world"}
    result = truncate_field(rec, "msg", 8)
    assert result["msg"] == "hello..."


def test_truncate_field_leaves_short_value_unchanged():
    rec = {"msg": "hi"}
    result = truncate_field(rec, "msg", 10)
    assert result["msg"] == "hi"


def test_truncate_field_exact_length_unchanged():
    rec = {"msg": "hello"}
    result = truncate_field(rec, "msg", 5)
    assert result["msg"] == "hello"


def test_truncate_field_does_not_mutate_original():
    rec = {"msg": "a very long message indeed"}
    _ = truncate_field(rec, "msg", 5)
    assert rec["msg"] == "a very long message indeed"


def test_truncate_field_custom_ellipsis():
    rec = {"msg": "abcdefgh"}
    result = truncate_field(rec, "msg", 5, ellipsis=">")
    assert result["msg"] == "abcd>"


def test_truncate_field_non_string_value_unchanged():
    rec = {"count": 12345}
    result = truncate_field(rec, "count", 3)
    assert result["count"] == 12345


def test_truncate_field_missing_field_raises():
    with pytest.raises(TruncatorError, match="not found"):
        truncate_field({"a": "x"}, "b", 5)


def test_truncate_field_empty_field_name_raises():
    with pytest.raises(TruncatorError, match="empty"):
        truncate_field({"a": "x"}, "", 5)


def test_truncate_field_zero_max_length_raises():
    with pytest.raises(TruncatorError, match="max_length"):
        truncate_field({"a": "x"}, "a", 0)


# ---------------------------------------------------------------------------
# truncate_all_fields
# ---------------------------------------------------------------------------

def test_truncate_all_fields_truncates_every_string():
    rec = {"a": "hello world", "b": "another long string"}
    result = truncate_all_fields(rec, 8)
    assert result["a"] == "hello..."
    assert result["b"] == "another."


def test_truncate_all_fields_skips_listed_fields():
    rec = {"a": "hello world", "b": "hello world"}
    result = truncate_all_fields(rec, 8, skip_fields=["b"])
    assert result["a"] == "hello..."
    assert result["b"] == "hello world"


def test_truncate_all_fields_invalid_max_length_raises():
    with pytest.raises(TruncatorError):
        truncate_all_fields({"a": "x"}, 0)


# ---------------------------------------------------------------------------
# apply_truncations
# ---------------------------------------------------------------------------

def test_apply_truncations_single_field():
    records = [{"msg": "a long message", "level": "info"}]
    result = apply_truncations(records, field="msg", max_length=6)
    assert result[0]["msg"] == "a l..."
    assert result[0]["level"] == "info"


def test_apply_truncations_all_fields():
    records = [{"msg": "long message", "source": "some/long/path"}]
    result = apply_truncations(records, max_length=8)
    assert result[0]["msg"] == "long ..."
    assert result[0]["source"] == "some/..."


def test_apply_truncations_returns_new_list():
    records = [{"msg": "hello world"}]
    result = apply_truncations(records, max_length=5)
    assert result is not records
    assert records[0]["msg"] == "hello world"
