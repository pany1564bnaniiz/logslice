"""Integration-level tests for merge_files in logslice.merger."""

import json
import pytest
from logslice.merger import merge_files, MergerError


def _write_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")


def test_merge_files_sorted(tmp_path):
    f1 = str(tmp_path / "a.jsonl")
    f2 = str(tmp_path / "b.jsonl")
    _write_jsonl(f1, [
        {"timestamp": "2024-01-01T00:00:01Z", "level": "info"},
        {"timestamp": "2024-01-01T00:00:05Z", "level": "warn"},
    ])
    _write_jsonl(f2, [
        {"timestamp": "2024-01-01T00:00:03Z", "level": "error"},
    ])
    result = list(merge_files([f1, f2], sort=True))
    levels = [r["level"] for r in result]
    assert levels == ["info", "error", "warn"]


def test_merge_files_unsorted(tmp_path):
    f1 = str(tmp_path / "a.jsonl")
    f2 = str(tmp_path / "b.jsonl")
    _write_jsonl(f1, [{"timestamp": "2024-01-01T00:00:05Z", "v": 5}])
    _write_jsonl(f2, [{"timestamp": "2024-01-01T00:00:01Z", "v": 1}])
    result = list(merge_files([f1, f2], sort=False))
    # round-robin: f1 first
    assert result[0]["v"] == 5
    assert result[1]["v"] == 1


def test_merge_files_no_paths_raises():
    with pytest.raises(MergerError):
        list(merge_files([]))


def test_merge_files_skips_malformed_lines(tmp_path):
    f1 = str(tmp_path / "bad.jsonl")
    with open(f1, "w") as fh:
        fh.write("not-json\n")
        fh.write(json.dumps({"timestamp": "2024-01-01T00:00:01Z", "ok": True}) + "\n")
    f2 = str(tmp_path / "good.jsonl")
    _write_jsonl(f2, [{"timestamp": "2024-01-01T00:00:02Z", "ok": True}])
    result = list(merge_files([f1, f2], sort=True))
    # malformed line skipped; 2 valid records remain
    assert len(result) == 2
    assert all(r["ok"] for r in result)


def test_merge_files_empty_file(tmp_path):
    f1 = str(tmp_path / "empty.jsonl")
    f2 = str(tmp_path / "data.jsonl")
    open(f1, "w").close()
    _write_jsonl(f2, [{"timestamp": "2024-01-01T00:00:01Z", "msg": "only"}])
    result = list(merge_files([f1, f2], sort=True))
    assert len(result) == 1
    assert result[0]["msg"] == "only"
