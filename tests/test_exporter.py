"""Tests for logslice/exporter.py."""

import json
import csv
import io
import pytest

from logslice.exporter import (
    ExportError,
    export_jsonl,
    export_csv,
    export_tsv,
    export_records,
)

SAMPLE = [
    {"level": "info", "msg": "started", "ts": "2024-01-01T00:00:00Z"},
    {"level": "error", "msg": "failed", "ts": "2024-01-01T00:01:00Z"},
]


# --- export_jsonl ---

def test_export_jsonl_produces_two_lines():
    result = export_jsonl(SAMPLE)
    lines = result.split("\n")
    assert len(lines) == 2


def test_export_jsonl_each_line_is_valid_json():
    result = export_jsonl(SAMPLE)
    for line in result.split("\n"):
        parsed = json.loads(line)
        assert isinstance(parsed, dict)


def test_export_jsonl_empty_list_returns_empty_string():
    assert export_jsonl([]) == ""


def test_export_jsonl_invalid_input_raises():
    with pytest.raises(ExportError):
        export_jsonl("not a list")  # type: ignore


# --- export_csv ---

def test_export_csv_has_header_row():
    result = export_csv(SAMPLE, fieldnames=["level", "msg", "ts"])
    lines = result.strip().split("\n")
    assert lines[0] == "level,msg,ts"


def test_export_csv_correct_number_of_rows():
    result = export_csv(SAMPLE, fieldnames=["level", "msg", "ts"])
    lines = result.strip().split("\n")
    assert len(lines) == 3  # header + 2 data rows


def test_export_csv_auto_fieldnames_sorted():
    result = export_csv(SAMPLE)
    reader = csv.DictReader(io.StringIO(result))
    assert reader.fieldnames == ["level", "msg", "ts"]


def test_export_csv_missing_field_fills_empty():
    records = [{"level": "info"}, {"level": "warn", "msg": "oops"}]
    result = export_csv(records, fieldnames=["level", "msg"])
    rows = list(csv.DictReader(io.StringIO(result)))
    assert rows[0]["msg"] == ""
    assert rows[1]["msg"] == "oops"


def test_export_csv_empty_records_returns_empty_string():
    assert export_csv([]) == ""


def test_export_csv_invalid_input_raises():
    with pytest.raises(ExportError):
        export_csv(None)  # type: ignore


# --- export_tsv ---

def test_export_tsv_uses_tab_delimiter():
    result = export_tsv(SAMPLE, fieldnames=["level", "msg", "ts"])
    header = result.split("\n")[0]
    assert "\t" in header
    assert "," not in header


# --- export_records ---

def test_export_records_jsonl():
    result = export_records(SAMPLE, "jsonl")
    assert len(result.split("\n")) == 2


def test_export_records_csv():
    result = export_records(SAMPLE, "csv", fieldnames=["level", "msg"])
    assert "level,msg" in result


def test_export_records_tsv():
    result = export_records(SAMPLE, "tsv", fieldnames=["level", "msg"])
    assert "level\tmsg" in result


def test_export_records_case_insensitive():
    result = export_records(SAMPLE, "JSONL")
    assert result


def test_export_records_unknown_format_raises():
    with pytest.raises(ExportError, match="Unsupported export format"):
        export_records(SAMPLE, "xml")
