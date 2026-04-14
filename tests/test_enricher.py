"""Tests for logslice.enricher."""

from __future__ import annotations

import pytest

from logslice.enricher import (
    EnricherError,
    apply_enrichments,
    enrich_with_callable,
    enrich_with_lookup,
    enrich_with_regex,
)


# ---------------------------------------------------------------------------
# enrich_with_regex
# ---------------------------------------------------------------------------

def test_enrich_with_regex_basic():
    rec = {"msg": "user=alice action=login"}
    out = enrich_with_regex(rec, "msg", r"user=(\w+)", "user")
    assert out["user"] == "alice"


def test_enrich_with_regex_no_match_uses_default():
    rec = {"msg": "nothing here"}
    out = enrich_with_regex(rec, "msg", r"user=(\w+)", "user", default="unknown")
    assert out["user"] == "unknown"


def test_enrich_with_regex_missing_source_uses_default():
    rec = {"level": "info"}
    out = enrich_with_regex(rec, "msg", r"user=(\w+)", "user", default="n/a")
    assert out["user"] == "n/a"


def test_enrich_with_regex_does_not_mutate_original():
    rec = {"msg": "user=bob"}
    enrich_with_regex(rec, "msg", r"user=(\w+)", "user")
    assert "user" not in rec


def test_enrich_with_regex_empty_source_field_raises():
    with pytest.raises(EnricherError):
        enrich_with_regex({}, "", r"(\w+)", "target")


def test_enrich_with_regex_empty_target_field_raises():
    with pytest.raises(EnricherError):
        enrich_with_regex({"msg": "hi"}, "msg", r"(\w+)", "")


def test_enrich_with_regex_empty_pattern_raises():
    with pytest.raises(EnricherError):
        enrich_with_regex({"msg": "hi"}, "msg", "", "target")


# ---------------------------------------------------------------------------
# enrich_with_lookup
# ---------------------------------------------------------------------------

def test_enrich_with_lookup_basic():
    rec = {"code": "200"}
    out = enrich_with_lookup(rec, "code", {"200": "OK", "404": "Not Found"}, "status_text")
    assert out["status_text"] == "OK"


def test_enrich_with_lookup_missing_key_uses_default():
    rec = {"code": "500"}
    out = enrich_with_lookup(rec, "code", {"200": "OK"}, "status_text", default="Unknown")
    assert out["status_text"] == "Unknown"


def test_enrich_with_lookup_missing_source_field_uses_default():
    rec = {"level": "info"}
    out = enrich_with_lookup(rec, "code", {"200": "OK"}, "status_text", default="-")
    assert out["status_text"] == "-"


def test_enrich_with_lookup_empty_source_field_raises():
    with pytest.raises(EnricherError):
        enrich_with_lookup({}, "  ", {}, "target")


def test_enrich_with_lookup_non_dict_raises():
    with pytest.raises(EnricherError):
        enrich_with_lookup({"x": "1"}, "x", "not-a-dict", "target")  # type: ignore


# ---------------------------------------------------------------------------
# enrich_with_callable
# ---------------------------------------------------------------------------

def test_enrich_with_callable_basic():
    rec = {"a": 3, "b": 4}
    out = enrich_with_callable(rec, "sum", lambda r: r["a"] + r["b"])
    assert out["sum"] == 7


def test_enrich_with_callable_does_not_mutate_original():
    rec = {"x": 1}
    enrich_with_callable(rec, "y", lambda r: r["x"] * 2)
    assert "y" not in rec


def test_enrich_with_callable_empty_target_raises():
    with pytest.raises(EnricherError):
        enrich_with_callable({}, "", lambda r: r)


def test_enrich_with_callable_non_callable_raises():
    with pytest.raises(EnricherError):
        enrich_with_callable({}, "field", "not-callable")  # type: ignore


# ---------------------------------------------------------------------------
# apply_enrichments
# ---------------------------------------------------------------------------

def test_apply_enrichments_chains_multiple():
    records = [{"msg": "user=carol action=logout"}]
    enrichments = [
        lambda r: enrich_with_regex(r, "msg", r"user=(\w+)", "user"),
        lambda r: enrich_with_regex(r, "msg", r"action=(\w+)", "action"),
    ]
    out = apply_enrichments(records, enrichments)
    assert out[0]["user"] == "carol"
    assert out[0]["action"] == "logout"


def test_apply_enrichments_empty_records():
    assert apply_enrichments([], [lambda r: r]) == []


def test_apply_enrichments_empty_enrichments():
    records = [{"a": 1}]
    assert apply_enrichments(records, []) == [{"a": 1}]
