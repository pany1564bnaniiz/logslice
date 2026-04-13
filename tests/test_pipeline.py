"""Tests for logslice.pipeline module."""

import json
from typing import List

from logslice.pipeline import run_pipeline


def _run(lines: List[str], **kwargs) -> List[str]:
    return list(run_pipeline(lines, **kwargs))


JSON_LINES = [
    '{"timestamp":"2024-01-01T09:00:00Z","level":"DEBUG","msg":"boot"}',
    '{"timestamp":"2024-01-01T10:00:00Z","level":"INFO","msg":"started"}',
    '{"timestamp":"2024-01-01T11:00:00Z","level":"ERROR","msg":"crash"}',
    '{"timestamp":"2024-01-01T12:00:00Z","level":"INFO","msg":"recovered"}',
]


def test_pipeline_passes_all_records_with_no_filters():
    results = _run(JSON_LINES)
    assert len(results) == 4


def test_pipeline_filters_by_level():
    results = _run(JSON_LINES, level="INFO")
    assert len(results) == 2
    for r in results:
        assert json.loads(r)["level"] == "INFO"


def test_pipeline_filters_by_time_range():
    results = _run(
        JSON_LINES,
        start="2024-01-01T09:30:00Z",
        end="2024-01-01T11:30:00Z",
    )
    assert len(results) == 2


def test_pipeline_filters_by_field_pattern():
    results = _run(JSON_LINES, fields=["msg=crash"])
    assert len(results) == 1
    assert json.loads(results[0])["msg"] == "crash"


def test_pipeline_skips_blank_lines():
    lines = ["", "   ", JSON_LINES[0], ""]
    results = _run(lines)
    assert len(results) == 1


def test_pipeline_show_stats_returns_summary():
    results = _run(JSON_LINES, show_stats=True)
    assert len(results) == 1
    summary = results[0]
    assert "Total" in summary
    assert "4" in summary


def test_pipeline_show_stats_respects_filters():
    results = _run(JSON_LINES, level="INFO", show_stats=True)
    summary = results[0]
    assert "2" in summary


def test_pipeline_output_fmt_logfmt():
    results = _run(JSON_LINES[:1], output_fmt="logfmt")
    assert "=" in results[0]
    assert "json" not in results[0]
