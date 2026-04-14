"""Additional integration-style tests for apply_enrichments in logslice.enricher."""

from __future__ import annotations

from logslice.enricher import (
    apply_enrichments,
    enrich_with_callable,
    enrich_with_lookup,
    enrich_with_regex,
)


SAMPLE_RECORDS = [
    {"msg": "user=alice action=login",  "code": "200"},
    {"msg": "user=bob action=logout",   "code": "404"},
    {"msg": "no-match",                  "code": "500"},
]

STATUS_MAP = {"200": "OK", "404": "Not Found", "500": "Internal Server Error"}


def test_apply_enrichments_regex_all_records():
    enrichments = [lambda r: enrich_with_regex(r, "msg", r"user=(\w+)", "user", default="-")]
    out = apply_enrichments(SAMPLE_RECORDS, enrichments)
    assert out[0]["user"] == "alice"
    assert out[1]["user"] == "bob"
    assert out[2]["user"] == "-"


def test_apply_enrichments_lookup_all_records():
    enrichments = [lambda r: enrich_with_lookup(r, "code", STATUS_MAP, "status_text", default="Unknown")]
    out = apply_enrichments(SAMPLE_RECORDS, enrichments)
    assert out[0]["status_text"] == "OK"
    assert out[1]["status_text"] == "Not Found"
    assert out[2]["status_text"] == "Internal Server Error"


def test_apply_enrichments_combined_pipeline():
    enrichments = [
        lambda r: enrich_with_regex(r, "msg", r"user=(\w+)", "user", default="anon"),
        lambda r: enrich_with_lookup(r, "code", STATUS_MAP, "status_text", default="?"),
        lambda r: enrich_with_callable(r, "summary", lambda rec: f"{rec.get('user')}:{rec.get('status_text')}"),
    ]
    out = apply_enrichments(SAMPLE_RECORDS, enrichments)
    assert out[0]["summary"] == "alice:OK"
    assert out[1]["summary"] == "bob:Not Found"
    assert out[2]["summary"] == "anon:Internal Server Error"


def test_apply_enrichments_preserves_original_records():
    """apply_enrichments must not mutate the input records."""
    records = [{"msg": "user=eve"}]
    apply_enrichments(records, [lambda r: enrich_with_regex(r, "msg", r"user=(\w+)", "user")])
    assert "user" not in records[0]


def test_apply_enrichments_returns_new_list():
    records = [{"a": 1}]
    out = apply_enrichments(records, [])
    assert out is not records
