"""Tests for logslice.parser module."""

import pytest
from logslice.parser import (
    parse_json_line,
    parse_logfmt_line,
    detect_format,
    LogParseError,
)


# --- JSON parser tests ---

def test_parse_json_line_basic():
    line = '{"level": "info", "msg": "hello", "ts": "2024-01-01T00:00:00Z"}'
    result = parse_json_line(line)
    assert result["level"] == "info"
    assert result["msg"] == "hello"


def test_parse_json_line_strips_whitespace():
    line = '  {"level": "warn"}  '
    result = parse_json_line(line)
    assert result["level"] == "warn"


def test_parse_json_line_empty_raises():
    with pytest.raises(LogParseError, match="Empty line"):
        parse_json_line("   ")


def test_parse_json_line_invalid_json_raises():
    with pytest.raises(LogParseError, match="Invalid JSON"):
        parse_json_line("{not valid json}")


def test_parse_json_line_non_object_raises():
    with pytest.raises(LogParseError, match="JSON object"):
        parse_json_line('["a", "b"]')


# --- logfmt parser tests ---

def test_parse_logfmt_basic():
    line = "level=info msg=hello ts=2024-01-01T00:00:00Z"
    result = parse_logfmt_line(line)
    assert result["level"] == "info"
    assert result["msg"] == "hello"
    assert result["ts"] == "2024-01-01T00:00:00Z"


def test_parse_logfmt_quoted_value():
    line = 'level=error msg="something went wrong" code=500'
    result = parse_logfmt_line(line)
    assert result["msg"] == "something went wrong"
    assert result["code"] == "500"


def test_parse_logfmt_quoted_escaped():
    line = 'msg="say \\"hello\\""'
    result = parse_logfmt_line(line)
    assert result["msg"] == 'say "hello"'


def test_parse_logfmt_bare_key():
    line = "verbose level=debug"
    result = parse_logfmt_line(line)
    assert result["verbose"] == ""
    assert result["level"] == "debug"


def test_parse_logfmt_empty_raises():
    with pytest.raises(LogParseError, match="Empty line"):
        parse_logfmt_line("")


# --- detect_format tests ---

def test_detect_format_json():
    assert detect_format('{"level": "info"}') == "json"


def test_detect_format_logfmt():
    assert detect_format("level=info msg=hello") == "logfmt"


def test_detect_format_unknown():
    assert detect_format("some plain text line") is None


def test_detect_format_json_with_leading_space():
    assert detect_format('  {"x": 1}') == "json"
