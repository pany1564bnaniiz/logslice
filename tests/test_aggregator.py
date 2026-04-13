"""Tests for logslice.aggregator."""

import pytest

from logslice.aggregator import (
    AggregatorError,
    count_by,
    group_by,
    top_values,
)

RECORDS = [
    {"level": "info", "service": "api", "msg": "started"},
    {"level": "error", "service": "api", "msg": "crash"},
    {"level": "info", "service": "worker", "msg": "processing"},
    {"level": "warn", "service": "api", "msg": "slow"},
    {"level": "info", "service": "worker", "msg": "done"},
]


# --- group_by ---

def test_group_by_basic():
    groups = group_by(RECORDS, "level")
    assert set(groups.keys()) == {"info", "error", "warn"}
    assert len(groups["info"]) == 3
    assert len(groups["error"]) == 1


def test_group_by_missing_field_uses_missing_key():
    groups = group_by(RECORDS, "nonexistent")
    assert "__missing__" in groups
    assert len(groups["__missing__"]) == len(RECORDS)


def test_group_by_empty_field_raises():
    with pytest.raises(AggregatorError, match="must not be empty"):
        group_by(RECORDS, "")


def test_group_by_empty_records():
    groups = group_by([], "level")
    assert groups == {}


def test_group_by_preserves_records():
    groups = group_by(RECORDS, "service")
    api_msgs = [r["msg"] for r in groups["api"]]
    assert "started" in api_msgs
    assert "crash" in api_msgs


# --- count_by ---

def test_count_by_basic():
    counts = count_by(RECORDS, "level")
    assert counts["info"] == 3
    assert counts["error"] == 1
    assert counts["warn"] == 1


def test_count_by_service():
    counts = count_by(RECORDS, "service")
    assert counts["api"] == 3
    assert counts["worker"] == 2


def test_count_by_empty_field_raises():
    with pytest.raises(AggregatorError, match="must not be empty"):
        count_by(RECORDS, "")


def test_count_by_empty_records():
    counts = count_by([], "level")
    assert counts == {}


def test_count_by_missing_field():
    counts = count_by(RECORDS, "missing")
    assert counts.get("__missing__") == len(RECORDS)


# --- top_values ---

def test_top_values_returns_sorted_desc():
    results = top_values(RECORDS, "level")
    assert results[0] == ("info", 3)


def test_top_values_n_limits_results():
    results = top_values(RECORDS, "level", n=2)
    assert len(results) == 2


def test_top_values_n_larger_than_unique():
    results = top_values(RECORDS, "level", n=100)
    assert len(results) == 3


def test_top_values_empty_field_raises():
    with pytest.raises(AggregatorError, match="must not be empty"):
        top_values(RECORDS, "")


def test_top_values_invalid_n_raises():
    with pytest.raises(AggregatorError, match="n must be >= 1"):
        top_values(RECORDS, "level", n=0)


def test_top_values_empty_records():
    results = top_values([], "level")
    assert results == []
