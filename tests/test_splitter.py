"""Tests for logslice.splitter."""

from __future__ import annotations

import pytest

from logslice.splitter import SplitterError, split_by_field, split_by_predicate


RECORDS = [
    {"level": "info", "msg": "started"},
    {"level": "error", "msg": "boom"},
    {"level": "info", "msg": "done"},
    {"level": "warn", "msg": "slow"},
    {"msg": "no-level"},
]


def test_split_by_field_basic():
    buckets = split_by_field(RECORDS, "level")
    assert set(buckets.keys()) == {"info", "error", "warn", "__missing__"}


def test_split_by_field_counts():
    buckets = split_by_field(RECORDS, "level")
    assert len(buckets["info"]) == 2
    assert len(buckets["error"]) == 1
    assert len(buckets["warn"]) == 1
    assert len(buckets["__missing__"]) == 1


def test_split_by_field_custom_missing_key():
    buckets = split_by_field(RECORDS, "level", missing_key="unknown")
    assert "unknown" in buckets
    assert "__missing__" not in buckets


def test_split_by_field_empty_field_raises():
    with pytest.raises(SplitterError):
        split_by_field(RECORDS, "")


def test_split_by_field_whitespace_field_raises():
    with pytest.raises(SplitterError):
        split_by_field(RECORDS, "   ")


def test_split_by_field_empty_records_returns_empty():
    buckets = split_by_field([], "level")
    assert buckets == {}


def test_split_by_field_does_not_mutate_originals():
    original = [{"level": "info", "msg": "hi"}]
    buckets = split_by_field(original, "level")
    assert buckets["info"][0] is original[0]


def test_split_by_predicate_basic():
    preds = {
        "errors": lambda r: r.get("level") == "error",
        "infos": lambda r: r.get("level") == "info",
    }
    buckets = split_by_predicate(RECORDS, preds)
    assert len(buckets["errors"]) == 1
    assert len(buckets["infos"]) == 2


def test_split_by_predicate_default_bucket():
    preds = {"errors": lambda r: r.get("level") == "error"}
    buckets = split_by_predicate(RECORDS, preds, default_bucket="rest")
    assert "rest" in buckets
    # warn, two infos, and the record with no level => 4
    assert len(buckets["rest"]) == 4


def test_split_by_predicate_empty_predicates_raises():
    with pytest.raises(SplitterError):
        split_by_predicate(RECORDS, {})


def test_split_by_predicate_empty_records_returns_empty():
    preds = {"errors": lambda r: r.get("level") == "error"}
    buckets = split_by_predicate([], preds)
    assert buckets == {}


def test_split_by_predicate_first_match_wins():
    preds = {
        "first": lambda r: r.get("level") in ("info", "error"),
        "second": lambda r: r.get("level") == "error",
    }
    buckets = split_by_predicate(RECORDS, preds)
    # error should land in 'first', not 'second'
    assert len(buckets.get("first", [])) == 3
    assert "second" not in buckets
