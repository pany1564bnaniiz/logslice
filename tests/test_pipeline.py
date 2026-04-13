"""Tests for logslice.pipeline module."""

import io
import json

import pytest

from logslice.pipeline import run_pipeline


JSON_LINES = "\n".join([
    json.dumps({"time": "2024-01-15T09:00:00Z", "level": "debug", "msg": "init"}),
    json.dumps({"time": "2024-01-15T10:00:00Z", "level": "info", "msg": "running", "svc": "api"}),
    json.dumps({"time": "2024-01-15T11:00:00Z", "level": "error", "msg": "crash"}),
    "",  # blank line should be skipped
])

LOGFMT_LINES = "\n".join([
    'time=2024-01-15T09:00:00Z level=debug msg=init',
    'time=2024-01-15T10:00:00Z level=info msg=running svc=api',
])


def _run(lines: str, **kwargs) -> list:
    inp = io.StringIO(lines)
    out = io.StringIO()
    run_pipeline(inp, out, **kwargs)
    out.seek(0)
    return [json.loads(l) for l in out if l.strip()]


def test_pipeline_passes_all_records_with_no_filters():
    records = _run(JSON_LINES)
    assert len(records) == 3


def test_pipeline_filters_by_level():
    records = _run(JSON_LINES, level="error")
    assert len(records) == 1
    assert records[0]["msg"] == "crash"


def test_pipeline_filters_by_time_range():
    records = _run(JSON_LINES, start="2024-01-15T09:30:00Z", end="2024-01-15T10:30:00Z")
    assert len(records) == 1
    assert records[0]["level"] == "info"


def test_pipeline_filters_by_field_pattern():
    records = _run(JSON_LINES, field_pattern="svc=api")
    assert len(records) == 1
    assert records[0]["svc"] == "api"


def test_pipeline_returns_written_count():
    inp = io.StringIO(JSON_LINES)
    out = io.StringIO()
    count = run_pipeline(inp, out, level="info")
    assert count == 1


def test_pipeline_skips_unparseable_lines():
    bad = "not-json-at-all\n" + json.dumps({"level": "info", "msg": "ok"})
    records = _run(bad, fmt="json")
    assert len(records) == 1
    assert records[0]["msg"] == "ok"


def test_pipeline_logfmt_input():
    records = _run(LOGFMT_LINES, fmt="logfmt")
    assert len(records) == 2


def test_pipeline_pretty_output():
    inp = io.StringIO(JSON_LINES)
    out = io.StringIO()
    run_pipeline(inp, out, out_fmt="pretty", level="info")
    out.seek(0)
    content = out.read()
    assert "[INFO]" in content
    assert "running" in content


def test_pipeline_empty_stream_writes_nothing():
    inp = io.StringIO("")
    out = io.StringIO()
    count = run_pipeline(inp, out)
    assert count == 0
