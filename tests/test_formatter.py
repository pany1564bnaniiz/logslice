"""Tests for logslice.formatter module."""

import json
import pytest

from logslice.formatter import (
    FormatError,
    format_json,
    format_logfmt,
    format_pretty,
    format_record,
)


SAMPLE = {
    "time": "2024-01-15T10:00:00Z",
    "level": "info",
    "msg": "server started",
    "port": 8080,
}


def test_format_json_produces_valid_json():
    result = format_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed == SAMPLE


def test_format_json_with_indent():
    result = format_json(SAMPLE, indent=2)
    assert "\n" in result
    parsed = json.loads(result)
    assert parsed["level"] == "info"


def test_format_logfmt_simple_values():
    record = {"level": "warn", "port": 9090, "active": True}
    result = format_logfmt(record)
    assert "level=warn" in result
    assert "port=9090" in result
    assert "active=true" in result


def test_format_logfmt_quotes_values_with_spaces():
    record = {"msg": "hello world"}
    result = format_logfmt(record)
    assert 'msg="hello world"' in result


def test_format_logfmt_none_value():
    record = {"key": None}
    result = format_logfmt(record)
    assert "key=" in result


def test_format_logfmt_nested_dict():
    record = {"meta": {"region": "us-east"}}
    result = format_logfmt(record)
    assert "meta=" in result


def test_format_pretty_includes_all_parts():
    result = format_pretty(SAMPLE)
    assert "2024-01-15T10:00:00Z" in result
    assert "[INFO]" in result
    assert "server started" in result
    assert "port=8080" in result


def test_format_pretty_missing_fields():
    record = {"msg": "minimal"}
    result = format_pretty(record)
    assert "minimal" in result


def test_format_pretty_uses_timestamp_alias():
    record = {"timestamp": "2024-01-01T00:00:00Z", "msg": "boot"}
    result = format_pretty(record)
    assert "2024-01-01T00:00:00Z" in result


def test_format_record_dispatches_json():
    result = format_record(SAMPLE, fmt="json")
    assert json.loads(result) == SAMPLE


def test_format_record_dispatches_logfmt():
    result = format_record(SAMPLE, fmt="logfmt")
    assert "level=info" in result


def test_format_record_dispatches_pretty():
    result = format_record(SAMPLE, fmt="pretty")
    assert "[INFO]" in result


def test_format_record_invalid_format_raises():
    with pytest.raises(FormatError, match="Unsupported format"):
        format_record(SAMPLE, fmt="csv")
