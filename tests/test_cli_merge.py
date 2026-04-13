"""Tests for logslice.cli_merge."""

import argparse
import io
import json
import os
import tempfile

import pytest

from logslice.cli_merge import add_merge_args, run_merge


def _make_parser():
    p = argparse.ArgumentParser()
    add_merge_args(p)
    return p


def _write_jsonl(path: str, records: list) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def test_run_merge_sorted_output(tmp_path):
    f1 = str(tmp_path / "a.log")
    f2 = str(tmp_path / "b.log")
    _write_jsonl(f1, [
        {"timestamp": "2024-01-01T00:00:01Z", "msg": "first"},
        {"timestamp": "2024-01-01T00:00:03Z", "msg": "third"},
    ])
    _write_jsonl(f2, [
        {"timestamp": "2024-01-01T00:00:02Z", "msg": "second"},
    ])
    parser = _make_parser()
    args = parser.parse_args([f1, f2])
    out = io.StringIO()
    rc = run_merge(args, out=out)
    assert rc == 0
    lines = [l for l in out.getvalue().splitlines() if l.strip()]
    assert len(lines) == 3
    msgs = [json.loads(l)["msg"] for l in lines]
    assert msgs == ["first", "second", "third"]


def test_run_merge_no_sort_flag(tmp_path):
    f1 = str(tmp_path / "a.log")
    f2 = str(tmp_path / "b.log")
    _write_jsonl(f1, [{"timestamp": "2024-01-01T00:00:03Z", "msg": "late"}])
    _write_jsonl(f2, [{"timestamp": "2024-01-01T00:00:01Z", "msg": "early"}])
    parser = _make_parser()
    args = parser.parse_args(["--no-sort", f1, f2])
    out = io.StringIO()
    rc = run_merge(args, out=out)
    assert rc == 0
    lines = [l for l in out.getvalue().splitlines() if l.strip()]
    # round-robin: f1 first
    assert json.loads(lines[0])["msg"] == "late"


def test_run_merge_requires_two_files(tmp_path):
    f1 = str(tmp_path / "a.log")
    _write_jsonl(f1, [{"msg": "x"}])
    parser = _make_parser()
    args = parser.parse_args([f1])
    out = io.StringIO()
    rc = run_merge(args, out=out)
    assert rc == 1


def test_run_merge_missing_file_returns_error(tmp_path):
    f1 = str(tmp_path / "a.log")
    _write_jsonl(f1, [{"timestamp": "2024-01-01T00:00:01Z", "msg": "ok"}])
    parser = _make_parser()
    args = parser.parse_args([f1, "/nonexistent/file.log"])
    out = io.StringIO()
    rc = run_merge(args, out=out)
    assert rc == 1


def test_add_merge_args_defaults():
    parser = _make_parser()
    args = parser.parse_args(["a.log", "b.log"])
    assert args.no_sort is False
    assert args.timestamp_field == "timestamp"
    assert args.output_format == "json"
