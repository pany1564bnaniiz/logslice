"""Tests for logslice.annotator."""

import pytest

from logslice.annotator import (
    AnnotatorError,
    annotate_derived,
    annotate_static,
    apply_annotations,
)


# ---------------------------------------------------------------------------
# annotate_static
# ---------------------------------------------------------------------------

def test_annotate_static_adds_new_field():
    record = {"level": "info", "msg": "hello"}
    result = annotate_static(record, "source", "app1")
    assert result["source"] == "app1"


def test_annotate_static_does_not_mutate_original():
    record = {"level": "info"}
    annotate_static(record, "env", "prod")
    assert "env" not in record


def test_annotate_static_preserves_existing_fields():
    record = {"level": "warn", "msg": "oops"}
    result = annotate_static(record, "tag", "legacy")
    assert result["level"] == "warn"
    assert result["msg"] == "oops"


def test_annotate_static_overwrite_false_raises_on_existing():
    record = {"source": "old"}
    with pytest.raises(AnnotatorError, match="already exists"):
        annotate_static(record, "source", "new")


def test_annotate_static_overwrite_true_replaces_value():
    record = {"source": "old"}
    result = annotate_static(record, "source", "new", overwrite=True)
    assert result["source"] == "new"


def test_annotate_static_empty_field_raises():
    with pytest.raises(AnnotatorError, match="must not be empty"):
        annotate_static({"a": 1}, "", "value")


def test_annotate_static_whitespace_field_raises():
    with pytest.raises(AnnotatorError, match="must not be empty"):
        annotate_static({"a": 1}, "   ", "value")


# ---------------------------------------------------------------------------
# annotate_derived
# ---------------------------------------------------------------------------

def test_annotate_derived_adds_computed_field():
    record = {"level": "error", "msg": "boom"}
    result = annotate_derived(record, "upper_level", lambda r: r["level"].upper())
    assert result["upper_level"] == "ERROR"


def test_annotate_derived_does_not_mutate_original():
    record = {"x": 1}
    annotate_derived(record, "y", lambda r: r["x"] + 1)
    assert "y" not in record


def test_annotate_derived_overwrite_false_raises_on_existing():
    record = {"score": 5}
    with pytest.raises(AnnotatorError, match="already exists"):
        annotate_derived(record, "score", lambda r: 10)


def test_annotate_derived_overwrite_true_replaces():
    record = {"score": 5}
    result = annotate_derived(record, "score", lambda r: 99, overwrite=True)
    assert result["score"] == 99


def test_annotate_derived_fn_exception_raises_annotator_error():
    record = {"val": "not-a-number"}
    with pytest.raises(AnnotatorError, match="annotation function raised an error"):
        annotate_derived(record, "doubled", lambda r: int(r["val"]) * 2)


def test_annotate_derived_empty_field_raises():
    with pytest.raises(AnnotatorError, match="must not be empty"):
        annotate_derived({}, "", lambda r: 1)


# ---------------------------------------------------------------------------
# apply_annotations
# ---------------------------------------------------------------------------

def test_apply_annotations_static_value():
    records = [{"msg": "a"}, {"msg": "b"}]
    result = apply_annotations(records, [{"field": "env", "value": "staging"}])
    assert all(r["env"] == "staging" for r in result)


def test_apply_annotations_derived_fn():
    records = [{"level": "info"}, {"level": "error"}]
    result = apply_annotations(
        records, [{"field": "upper", "fn": lambda r: r["level"].upper()}]
    )
    assert result[0]["upper"] == "INFO"
    assert result[1]["upper"] == "ERROR"


def test_apply_annotations_multiple_specs():
    records = [{"msg": "hi"}]
    specs = [
        {"field": "env", "value": "prod"},
        {"field": "tagged", "value": True},
    ]
    result = apply_annotations(records, specs)
    assert result[0]["env"] == "prod"
    assert result[0]["tagged"] is True


def test_apply_annotations_empty_records_returns_empty():
    result = apply_annotations([], [{"field": "x", "value": 1}])
    assert result == []


def test_apply_annotations_both_value_and_fn_raises():
    records = [{"a": 1}]
    with pytest.raises(AnnotatorError, match="must not specify both"):
        apply_annotations(records, [{"field": "x", "value": 1, "fn": lambda r: 2}])


def test_apply_annotations_neither_value_nor_fn_raises():
    records = [{"a": 1}]
    with pytest.raises(AnnotatorError, match="must specify either"):
        apply_annotations(records, [{"field": "x"}])
