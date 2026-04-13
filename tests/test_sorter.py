"""Tests for logslice.sorter."""

import pytest

from logslice.sorter import SorterError, sort_records, sort_by_timestamp


RECORDS = [
    {"level": "error", "timestamp": "2024-01-03T10:00:00Z", "msg": "c"},
    {"level": "info",  "timestamp": "2024-01-01T08:00:00Z", "msg": "a"},
    {"level": "warn",  "timestamp": "2024-01-02T09:00:00Z", "msg": "b"},
]


def test_sort_records_ascending():
    result = sort_records(RECORDS, field="msg")
    assert [r["msg"] for r in result] == ["a", "b", "c"]


def test_sort_records_descending():
    result = sort_records(RECORDS, field="msg", reverse=True)
    assert [r["msg"] for r in result] == ["c", "b", "a"]


def test_sort_records_does_not_mutate_original():
    original = list(RECORDS)
    sort_records(RECORDS, field="msg")
    assert RECORDS == original


def test_sort_records_empty_field_raises():
    with pytest.raises(SorterError):
        sort_records(RECORDS, field="")


def test_sort_records_whitespace_field_raises():
    with pytest.raises(SorterError):
        sort_records(RECORDS, field="   ")


def test_sort_records_missing_field_goes_last():
    records = [
        {"level": "info", "score": "10"},
        {"level": "warn"},
        {"level": "error", "score": "5"},
    ]
    result = sort_records(records, field="score")
    assert result[-1]["level"] == "warn"


def test_sort_records_empty_list():
    assert sort_records([], field="msg") == []


def test_sort_by_timestamp_ascending():
    result = sort_by_timestamp(RECORDS)
    assert result[0]["timestamp"] == "2024-01-01T08:00:00Z"
    assert result[-1]["timestamp"] == "2024-01-03T10:00:00Z"


def test_sort_by_timestamp_descending():
    result = sort_by_timestamp(RECORDS, reverse=True)
    assert result[0]["timestamp"] == "2024-01-03T10:00:00Z"


def test_sort_by_timestamp_custom_field():
    records = [
        {"ts": "2024-03-01"},
        {"ts": "2024-01-01"},
        {"ts": "2024-02-01"},
    ]
    result = sort_by_timestamp(records, timestamp_field="ts")
    assert [r["ts"] for r in result] == ["2024-01-01", "2024-02-01", "2024-03-01"]


def test_sort_by_timestamp_empty_field_raises():
    with pytest.raises(SorterError):
        sort_by_timestamp(RECORDS, timestamp_field="")
