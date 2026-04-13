"""Tests for logslice.redactor."""

import pytest

from logslice.redactor import (
    RedactorError,
    apply_redactions,
    redact_field,
    redact_pattern,
)


# ---------------------------------------------------------------------------
# redact_field
# ---------------------------------------------------------------------------

def test_redact_field_replaces_value():
    record = {"user": "alice", "msg": "hello"}
    result = redact_field(record, "user")
    assert result["user"] == "***"


def test_redact_field_custom_mask():
    record = {"token": "secret123"}
    result = redact_field(record, "token", mask="[REDACTED]")
    assert result["token"] == "[REDACTED]"


def test_redact_field_does_not_mutate_original():
    record = {"password": "hunter2"}
    redact_field(record, "password")
    assert record["password"] == "hunter2"


def test_redact_field_missing_key_raises():
    with pytest.raises(RedactorError, match="not found"):
        redact_field({"a": 1}, "b")


def test_redact_field_empty_field_name_raises():
    with pytest.raises(RedactorError, match="must not be empty"):
        redact_field({"a": 1}, "")


def test_redact_field_preserves_other_fields():
    record = {"user": "alice", "level": "info", "msg": "ok"}
    result = redact_field(record, "user")
    assert result["level"] == "info"
    assert result["msg"] == "ok"


# ---------------------------------------------------------------------------
# redact_pattern
# ---------------------------------------------------------------------------

def test_redact_pattern_replaces_match():
    record = {"msg": "user email is foo@example.com today"}
    result = redact_pattern(record, r"[\w.+-]+@[\w-]+\.[\w.]+")
    assert "foo@example.com" not in result["msg"]
    assert "***" in result["msg"]


def test_redact_pattern_limited_to_fields():
    record = {"msg": "token=abc123", "safe": "token=abc123"}
    result = redact_pattern(record, r"abc123", fields=["msg"])
    assert "***" in result["msg"]
    assert result["safe"] == "token=abc123"


def test_redact_pattern_skips_non_string_fields():
    record = {"count": 42, "msg": "hello 42"}
    result = redact_pattern(record, r"42")
    assert result["count"] == 42  # integer untouched
    assert "***" in result["msg"]


def test_redact_pattern_invalid_regex_raises():
    with pytest.raises(RedactorError, match="invalid pattern"):
        redact_pattern({"msg": "hi"}, r"[unclosed")


def test_redact_pattern_empty_pattern_raises():
    with pytest.raises(RedactorError, match="must not be empty"):
        redact_pattern({"msg": "hi"}, "")


# ---------------------------------------------------------------------------
# apply_redactions
# ---------------------------------------------------------------------------

def test_apply_redactions_field_list():
    records = [{"user": "alice", "msg": "a"}, {"user": "bob", "msg": "b"}]
    results = apply_redactions(records, redact_fields=["user"])
    assert all(r["user"] == "***" for r in results)
    assert results[0]["msg"] == "a"


def test_apply_redactions_pattern():
    records = [{"msg": "ip 192.168.1.1 connected"}]
    results = apply_redactions(records, redact_pattern_str=r"\d+\.\d+\.\d+\.\d+")
    assert "192.168.1.1" not in results[0]["msg"]


def test_apply_redactions_missing_field_skipped():
    records = [{"msg": "hello"}, {"user": "alice", "msg": "world"}]
    results = apply_redactions(records, redact_fields=["user"])
    assert results[0].get("user") is None
    assert results[1]["user"] == "***"


def test_apply_redactions_does_not_mutate_originals():
    records = [{"token": "secret"}]
    apply_redactions(records, redact_fields=["token"])
    assert records[0]["token"] == "secret"


def test_apply_redactions_empty_records():
    assert apply_redactions([]) == []
