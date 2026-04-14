"""Tests for logslice.cli_enrich."""

from __future__ import annotations

import argparse
import json
from io import StringIO
from unittest.mock import patch

import pytest

from logslice.cli_enrich import (
    _parse_lookup_spec,
    _parse_regex_spec,
    add_enrich_args,
    run_enrich,
)


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_enrich_args(sub)
    return parser


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = {
        "input": "-",
        "regex": [],
        "lookup": [],
        "output_format": "json",
        "func": run_enrich,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# arg parsing helpers
# ---------------------------------------------------------------------------

def test_add_enrich_args_registers_subcommand():
    parser = _make_parser()
    ns = parser.parse_args(["enrich"])
    assert ns.func is run_enrich


def test_add_enrich_args_default_output_format():
    parser = _make_parser()
    ns = parser.parse_args(["enrich"])
    assert ns.output_format == "json"


def test_parse_regex_spec_valid():
    src, pat, tgt = _parse_regex_spec("msg:user=(\\w+):user")
    assert src == "msg" and tgt == "user"


def test_parse_regex_spec_invalid_raises():
    with pytest.raises(ValueError):
        _parse_regex_spec("only:two")


def test_parse_lookup_spec_valid():
    src, mapping, tgt = _parse_lookup_spec('code:{"200":"OK"}:status')
    assert src == "code"
    assert mapping == {"200": "OK"}
    assert tgt == "status"


def test_parse_lookup_spec_invalid_json_raises():
    with pytest.raises(ValueError, match="Invalid JSON"):
        _parse_lookup_spec("code:not-json:status")


def test_parse_lookup_spec_non_object_raises():
    with pytest.raises(ValueError, match="JSON object"):
        _parse_lookup_spec('code:[1,2]:status')


# ---------------------------------------------------------------------------
# run_enrich integration
# ---------------------------------------------------------------------------

def test_run_enrich_regex_enrichment(capsys):
    line = json.dumps({"msg": "user=dave action=login"}) + "\n"
    args = _make_args(regex=["msg:user=(\\w+):user"])
    with patch("sys.stdin", StringIO(line)):
        run_enrich(args)
    captured = capsys.readouterr().out
    record = json.loads(captured.strip())
    assert record["user"] == "dave"


def test_run_enrich_lookup_enrichment(capsys):
    line = json.dumps({"code": "200"}) + "\n"
    args = _make_args(lookup=['code:{"200":"OK"}:status_text'])
    with patch("sys.stdin", StringIO(line)):
        run_enrich(args)
    captured = capsys.readouterr().out
    record = json.loads(captured.strip())
    assert record["status_text"] == "OK"


def test_run_enrich_skips_blank_lines(capsys):
    data = "\n" + json.dumps({"x": 1}) + "\n\n"
    args = _make_args()
    with patch("sys.stdin", StringIO(data)):
        run_enrich(args)
    lines = [l for l in capsys.readouterr().out.strip().splitlines() if l]
    assert len(lines) == 1


def test_run_enrich_passes_through_without_specs(capsys):
    line = json.dumps({"level": "info", "msg": "hello"}) + "\n"
    args = _make_args()
    with patch("sys.stdin", StringIO(line)):
        run_enrich(args)
    record = json.loads(capsys.readouterr().out.strip())
    assert record["level"] == "info"
