"""Tests for logslice.merger."""

import pytest
from logslice.merger import (
    MergerError,
    merge_sorted,
    merge_records,
)


A = [
    {"timestamp": "2024-01-01T00:00:01Z", "msg": "a1"},
    {"timestamp": "2024-01-01T00:00:03Z", "msg": "a3"},
    {"timestamp": "2024-01-01T00:00:05Z", "msg": "a5"},
]

B = [
    {"timestamp": "2024-01-01T00:00:02Z", "msg": "b2"},
    {"timestamp": "2024-01-01T00:00:04Z", "msg": "b4"},
    {"timestamp": "2024-01-01T00:00:06Z", "msg": "b6"},
]


def test_merge_sorted_interleaves_correctly():
    result = list(merge_sorted([A, B]))
    msgs = [r["msg"] for r in result]
    assert msgs == ["a1", "b2", "a3", "b4", "a5", "b6"]


def test_merge_sorted_single_stream():
    result = list(merge_sorted([A]))
    assert result == A


def test_merge_sorted_empty_streams():
    result = list(merge_sorted([]))
    assert result == []


def test_merge_sorted_one_empty_stream():
    result = list(merge_sorted([A, []]))
    assert result == A


def test_merge_sorted_records_without_timestamp_appended_last():
    no_ts = [{"msg": "no-ts"}]
    result = list(merge_sorted([A, no_ts]))
    assert result[-1] == {"msg": "no-ts"}
    assert len(result) == len(A) + 1


def test_merge_sorted_custom_timestamp_field():
    stream1 = [{"t": "2024-01-01T01:00:00Z", "v": 1}]
    stream2 = [{"t": "2024-01-01T00:30:00Z", "v": 2}]
    result = list(merge_sorted([stream1, stream2], timestamp_field="t"))
    assert result[0]["v"] == 2
    assert result[1]["v"] == 1


def test_merge_sorted_invalid_timestamp_field_raises():
    with pytest.raises(MergerError):
        list(merge_sorted([A], timestamp_field=""))


def test_merge_sorted_whitespace_timestamp_field_raises():
    with pytest.raises(MergerError):
        list(merge_sorted([A], timestamp_field="   "))


def test_merge_records_round_robin():
    s1 = [{"v": 1}, {"v": 3}]
    s2 = [{"v": 2}, {"v": 4}]
    result = list(merge_records([s1, s2]))
    assert [r["v"] for r in result] == [1, 2, 3, 4]


def test_merge_records_empty_streams():
    assert list(merge_records([])) == []


def test_merge_records_unequal_lengths():
    s1 = [{"v": 1}, {"v": 2}, {"v": 3}]
    s2 = [{"v": 10}]
    result = list(merge_records([s1, s2]))
    assert {r["v"] for r in result} == {1, 2, 3, 10}
    assert len(result) == 4


def test_merge_records_does_not_mutate_originals():
    s1 = [{"v": 1}]
    s2 = [{"v": 2}]
    original_s1 = list(s1)
    original_s2 = list(s2)
    list(merge_records([s1, s2]))
    assert s1 == original_s1
    assert s2 == original_s2
