"""Tests for logslice.profiler."""

import pytest

from logslice.profiler import ProfilerError, _infer_type, profile_field, profile_records


RECORDS = [
    {"level": "info", "status": "200", "latency": 12},
    {"level": "error", "status": "500", "latency": 300},
    {"level": "info", "status": "200", "latency": 8},
    {"level": "warn", "status": "404"},
    {"level": "info"},
]


# --- _infer_type ---

def test_infer_type_none():
    assert _infer_type(None) == "null"

def test_infer_type_bool():
    assert _infer_type(True) == "bool"

def test_infer_type_int():
    assert _infer_type(42) == "int"

def test_infer_type_float():
    assert _infer_type(3.14) == "float"

def test_infer_type_str():
    assert _infer_type("hello") == "str"

def test_infer_type_list():
    assert _infer_type([1, 2]) == "list"

def test_infer_type_dict():
    assert _infer_type({"a": 1}) == "dict"


# --- profile_field ---

def test_profile_field_present_count():
    result = profile_field(RECORDS, "level")
    assert result["present"] == 5
    assert result["missing"] == 0

def test_profile_field_missing_count():
    result = profile_field(RECORDS, "latency")
    assert result["present"] == 3
    assert result["missing"] == 2

def test_profile_field_coverage_full():
    result = profile_field(RECORDS, "level")
    assert result["coverage"] == 1.0

def test_profile_field_coverage_partial():
    result = profile_field(RECORDS, "latency")
    assert result["coverage"] == pytest.approx(0.6, rel=1e-3)

def test_profile_field_top_values_most_common_first():
    result = profile_field(RECORDS, "level", top_n=3)
    top = [v for v, _ in result["top_values"]]
    assert top[0] == "info"

def test_profile_field_types_recorded():
    result = profile_field(RECORDS, "latency")
    assert "int" in result["types"]

def test_profile_field_total_equals_record_count():
    result = profile_field(RECORDS, "status")
    assert result["total"] == len(RECORDS)

def test_profile_field_empty_field_raises():
    with pytest.raises(ProfilerError, match="non-empty"):
        profile_field(RECORDS, "")

def test_profile_field_whitespace_field_raises():
    with pytest.raises(ProfilerError, match="non-empty"):
        profile_field(RECORDS, "   ")

def test_profile_field_invalid_top_n_raises():
    with pytest.raises(ProfilerError, match="top_n"):
        profile_field(RECORDS, "level", top_n=0)

def test_profile_field_empty_records():
    result = profile_field([], "level")
    assert result["present"] == 0
    assert result["coverage"] == 0.0


# --- profile_records ---

def test_profile_records_total():
    result = profile_records(RECORDS)
    assert result["total_records"] == 5

def test_profile_records_all_fields_present():
    result = profile_records(RECORDS)
    assert "level" in result["fields"]
    assert "status" in result["fields"]
    assert "latency" in result["fields"]

def test_profile_records_empty_input():
    result = profile_records([])
    assert result["total_records"] == 0
    assert result["fields"] == {}

def test_profile_records_field_keys_sorted():
    result = profile_records(RECORDS)
    keys = list(result["fields"].keys())
    assert keys == sorted(keys)
