"""Tests for logslice.highlighter."""

import pytest

from logslice.highlighter import (
    HighlightError,
    highlight_field_value,
    highlight_level,
    highlight_record,
    ANSI_RESET,
    ANSI_RED,
    ANSI_GREEN,
    ANSI_YELLOW,
    ANSI_DIM,
    ANSI_MAGENTA,
    ANSI_BOLD,
)


def test_highlight_level_error_is_red():
    record = {"level": "error", "msg": "boom"}
    result = highlight_level(record)
    assert ANSI_RED in result
    assert "error" in result
    assert ANSI_RESET in result


def test_highlight_level_info_is_green():
    record = {"level": "info"}
    result = highlight_level(record)
    assert ANSI_GREEN in result


def test_highlight_level_warn_is_yellow():
    record = {"level": "warn"}
    result = highlight_level(record)
    assert ANSI_YELLOW in result


def test_highlight_level_debug_is_dim():
    record = {"level": "debug"}
    result = highlight_level(record)
    assert ANSI_DIM in result


def test_highlight_level_unknown_returns_plain():
    record = {"level": "verbose"}
    result = highlight_level(record)
    assert result == "verbose"


def test_highlight_level_missing_field_returns_empty():
    record = {"msg": "hello"}
    result = highlight_level(record)
    assert result == ""


def test_highlight_level_non_string_value_is_cast():
    record = {"level": 42}
    result = highlight_level(record)
    assert "42" in result


def test_highlight_field_value_wraps_match():
    result = highlight_field_value("hello world", r"world")
    assert ANSI_MAGENTA in result
    assert "world" in result
    assert ANSI_RESET in result


def test_highlight_field_value_no_match_returns_unchanged():
    result = highlight_field_value("hello world", r"zzz")
    assert result == "hello world"


def test_highlight_field_value_empty_pattern_raises():
    with pytest.raises(HighlightError, match="Pattern must not be empty"):
        highlight_field_value("hello", "")


def test_highlight_field_value_invalid_pattern_raises():
    with pytest.raises(HighlightError, match="Invalid pattern"):
        highlight_field_value("hello", "[invalid")


def test_highlight_field_value_non_string_value_cast():
    result = highlight_field_value(12345, r"23")
    assert "12345" in result
    assert ANSI_MAGENTA in result


def test_highlight_record_colorizes_level():
    record = {"level": "error", "msg": "oops"}
    result = highlight_record(record)
    assert ANSI_RED in result["level"]
    assert result["msg"] == "oops"


def test_highlight_record_applies_pattern_to_string_fields():
    record = {"level": "info", "msg": "user login failed"}
    result = highlight_record(record, highlight_pattern=r"failed")
    assert ANSI_MAGENTA in result["msg"]
    assert "failed" in result["msg"]


def test_highlight_record_skips_non_string_values_for_pattern():
    record = {"level": "info", "count": 99}
    result = highlight_record(record, highlight_pattern=r"9")
    assert result["count"] == 99


def test_highlight_record_does_not_mutate_original():
    record = {"level": "warn", "msg": "watch out"}
    original_msg = record["msg"]
    highlight_record(record, highlight_pattern=r"watch")
    assert record["msg"] == original_msg


def test_highlight_record_non_dict_raises():
    with pytest.raises(HighlightError, match="Record must be a dict"):
        highlight_record(["not", "a", "dict"])  # type: ignore
