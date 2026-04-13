"""Tests for logslice.filters module."""

import pytest
from datetime import datetime, timezone

from logslice.filters import (
    FilterError,
    filter_by_field_pattern,
    filter_by_level,
    filter_by_time,
)

UT = timezone.utc


# --- filter_by_time ---

def test_filter_by_time_no_constraints_passes():
    assert filter_by_time({"time": "2024-01-01T00:00:00Z"}) is True


def test_filter_by_time_within_range():
    start = datetime(2024, 1, 1, tzinfo=UT)
    end = datetime(2024, 1, 31, tzinfo=UT)
    assert filter_by_time({"time": "2024-01-15T12:00:00Z"}, start=start, end=end) is True


def test_filter_by_time_before_start_excluded():
    start = datetime(2024, 6, 1, tzinfo=UT)
    assert filter_by_time({"time": "2024-01-01T00:00:00Z"}, start=start) is False


def test_filter_by_time_after_end_excluded():
    end = datetime(2024, 1, 1, tzinfo=UT)
    assert filter_by_time({"time": "2024-06-01T00:00:00Z"}, end=end) is False


def test_filter_by_time_unix_timestamp():
    start = datetime(2024, 1, 1, tzinfo=UT)
    ts = start.timestamp()
    assert filter_by_time({"time": ts}, start=start) is True


def test_filter_by_time_missing_field_passes():
    assert filter_by_time({"msg": "hello"}, start=datetime(2024, 1, 1, tzinfo=UT)) is True


def test_filter_by_time_fallback_timestamp_field():
    start = datetime(2024, 1, 1, tzinfo=UT)
    assert filter_by_time({"timestamp": "2024-03-01T00:00:00Z"}, start=start) is True


# --- filter_by_level ---

def test_filter_by_level_no_levels_passes():
    assert filter_by_level({"level": "debug"}) is True


def test_filter_by_level_match():
    assert filter_by_level({"level": "error"}, levels=["error", "warn"]) is True


def test_filter_by_level_no_match():
    assert filter_by_level({"level": "debug"}, levels=["error", "warn"]) is False


def test_filter_by_level_case_insensitive():
    assert filter_by_level({"level": "ERROR"}, levels=["error"]) is True


def test_filter_by_level_missing_field_excluded():
    assert filter_by_level({"msg": "hello"}, levels=["info"]) is False


def test_filter_by_level_fallback_lvl_field():
    assert filter_by_level({"lvl": "warn"}, levels=["warn"]) is True


# --- filter_by_field_pattern ---

def test_filter_by_field_pattern_match():
    assert filter_by_field_pattern({"msg": "connection refused"}, "msg", "refused") is True


def test_filter_by_field_pattern_no_match():
    assert filter_by_field_pattern({"msg": "all good"}, "msg", "refused") is False


def test_filter_by_field_pattern_missing_field():
    assert filter_by_field_pattern({"level": "info"}, "msg", ".*") is False


def test_filter_by_field_pattern_regex():
    assert filter_by_field_pattern({"path": "/api/v2/users"}, "path", r"^/api/v\d+/") is True


def test_filter_by_field_pattern_invalid_regex_raises():
    with pytest.raises(FilterError, match="Invalid regex"):
        filter_by_field_pattern({"msg": "hello"}, "msg", "[invalid")
