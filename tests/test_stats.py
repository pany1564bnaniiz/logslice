"""Tests for logslice.stats module."""

import pytest
from logslice.stats import StatsError, compute_stats, format_stats


RECORDS = [
    {"timestamp": "2024-01-01T10:00:00Z", "level": "INFO",  "msg": "started"},
    {"timestamp": "2024-01-01T10:01:00Z", "level": "DEBUG", "msg": "running"},
    {"timestamp": "2024-01-01T10:02:00Z", "level": "ERROR", "msg": "failed"},
    {"timestamp": "2024-01-01T10:03:00Z", "level": "INFO",  "msg": "done"},
]


def test_compute_stats_total():
    stats = compute_stats(RECORDS)
    assert stats["total"] == 4


def test_compute_stats_by_level():
    stats = compute_stats(RECORDS)
    assert stats["by_level"] == {"INFO": 2, "DEBUG": 1, "ERROR": 1}


def test_compute_stats_fields():
    stats = compute_stats(RECORDS)
    assert "level" in stats["fields"]
    assert "msg" in stats["fields"]
    assert "timestamp" in stats["fields"]


def test_compute_stats_time_range():
    stats = compute_stats(RECORDS)
    assert stats["time_range"] is not None
    assert stats["time_range"]["min"] == "2024-01-01T10:00:00Z"
    assert stats["time_range"]["max"] == "2024-01-01T10:03:00Z"


def test_compute_stats_empty():
    stats = compute_stats([])
    assert stats["total"] == 0
    assert stats["by_level"] == {}
    assert stats["fields"] == []
    assert stats["time_range"] is None


def test_compute_stats_no_level_field():
    records = [{"msg": "hello"}, {"msg": "world"}]
    stats = compute_stats(records)
    assert stats["by_level"] == {}


def test_compute_stats_alternative_level_keys():
    records = [
        {"severity": "warn", "msg": "a"},
        {"lvl": "info",     "msg": "b"},
    ]
    stats = compute_stats(records)
    assert "WARN" in stats["by_level"]
    assert "INFO" in stats["by_level"]


def test_compute_stats_invalid_record_raises():
    with pytest.raises(StatsError):
        compute_stats(["not a dict"])  # type: ignore


def test_format_stats_contains_total():
    stats = compute_stats(RECORDS)
    output = format_stats(stats)
    assert "4" in output
    assert "Total" in output


def test_format_stats_contains_levels():
    stats = compute_stats(RECORDS)
    output = format_stats(stats)
    assert "INFO" in output
    assert "ERROR" in output


def test_format_stats_contains_time_range():
    stats = compute_stats(RECORDS)
    output = format_stats(stats)
    assert "2024-01-01T10:00:00Z" in output
    assert "2024-01-01T10:03:00Z" in output


def test_format_stats_no_timestamp():
    stats = compute_stats([{"msg": "hi"}])
    output = format_stats(stats)
    assert "no timestamp" in output
