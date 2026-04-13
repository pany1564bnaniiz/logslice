"""Tests for logslice.deduplicator."""

import pytest

from logslice.deduplicator import (
    DeduplicatorError,
    count_duplicates,
    deduplicate,
)


# --- deduplicate ---

def test_deduplicate_no_dupes_passes_all():
    records = [
        {"level": "info", "msg": "a"},
        {"level": "error", "msg": "b"},
    ]
    result = list(deduplicate(records))
    assert result == records


def test_deduplicate_removes_exact_duplicates():
    records = [
        {"level": "info", "msg": "hello"},
        {"level": "info", "msg": "hello"},
        {"level": "error", "msg": "oops"},
    ]
    result = list(deduplicate(records))
    assert len(result) == 2


def test_deduplicate_keeps_first_occurrence():
    records = [
        {"level": "info", "msg": "first"},
        {"level": "info", "msg": "first"},
    ]
    result = list(deduplicate(records))
    assert result[0]["msg"] == "first"
    assert len(result) == 1


def test_deduplicate_by_specific_fields():
    records = [
        {"level": "info", "msg": "a", "ts": "1"},
        {"level": "info", "msg": "a", "ts": "2"},  # same level+msg, different ts
    ]
    result = list(deduplicate(records, fields=["level", "msg"]))
    assert len(result) == 1


def test_deduplicate_by_specific_fields_keeps_distinct():
    records = [
        {"level": "info", "msg": "a"},
        {"level": "error", "msg": "a"},
    ]
    result = list(deduplicate(records, fields=["level"]))
    assert len(result) == 2


def test_deduplicate_empty_fields_list_raises():
    with pytest.raises(DeduplicatorError, match="must not be empty"):
        list(deduplicate([{"a": 1}], fields=[]))


def test_deduplicate_empty_records():
    result = list(deduplicate([]))
    assert result == []


def test_deduplicate_does_not_mutate_records():
    original = {"level": "info", "msg": "x"}
    records = [original, original]
    result = list(deduplicate(records))
    assert result[0] is original


# --- count_duplicates ---

def test_count_duplicates_none_when_all_unique():
    records = [{"a": 1}, {"a": 2}, {"a": 3}]
    assert count_duplicates(records) == 0


def test_count_duplicates_counts_correctly():
    records = [
        {"level": "info"},
        {"level": "info"},
        {"level": "info"},
        {"level": "error"},
    ]
    assert count_duplicates(records) == 2


def test_count_duplicates_by_fields():
    records = [
        {"level": "info", "ts": "1"},
        {"level": "info", "ts": "2"},
        {"level": "error", "ts": "3"},
    ]
    assert count_duplicates(records, fields=["level"]) == 1


def test_count_duplicates_empty_records():
    assert count_duplicates([]) == 0


def test_count_duplicates_empty_fields_raises():
    with pytest.raises(DeduplicatorError, match="must not be empty"):
        count_duplicates([{"a": 1}], fields=[])
