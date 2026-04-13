"""Tests for logslice.cli_annotate."""

import argparse
import json
from io import StringIO
from unittest.mock import patch

import pytest

from logslice.cli_annotate import add_annotate_args, run_annotate


def _make_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")
    add_annotate_args(sub)
    return parser


def _make_args(set_fields=None, input_file="-", output_format="json"):
    parser = _make_parser()
    argv = ["annotate"]
    for sf in set_fields or []:
        argv += ["--set", sf]
    if output_format != "json":
        argv += ["--output-format", output_format]
    if input_file != "-":
        argv.append(input_file)
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# add_annotate_args
# ---------------------------------------------------------------------------

def test_add_annotate_args_registers_subcommand():
    parser = _make_parser()
    args = parser.parse_args(["annotate"])
    assert args.command == "annotate"


def test_add_annotate_args_default_output_format():
    args = _make_args()
    assert args.output_format == "json"


def test_add_annotate_args_set_fields_collected():
    args = _make_args(set_fields=["env=prod", "version=2"])
    assert args.set_fields == ["env=prod", "version=2"]


# ---------------------------------------------------------------------------
# run_annotate — happy path via stdin mock
# ---------------------------------------------------------------------------

def test_run_annotate_adds_static_field(capsys):
    line = json.dumps({"level": "info", "msg": "hello"}) + "\n"
    args = _make_args(set_fields=["env=prod"])
    with patch("sys.stdin", StringIO(line)):
        rc = run_annotate(args)
    assert rc == 0
    out = capsys.readouterr().out
    record = json.loads(out.strip())
    assert record["env"] == "prod"
    assert record["level"] == "info"


def test_run_annotate_numeric_value_decoded(capsys):
    line = json.dumps({"msg": "hi"}) + "\n"
    args = _make_args(set_fields=["retries=3"])
    with patch("sys.stdin", StringIO(line)):
        run_annotate(args)
    out = capsys.readouterr().out
    record = json.loads(out.strip())
    assert record["retries"] == 3


def test_run_annotate_multiple_set_fields(capsys):
    line = json.dumps({"msg": "x"}) + "\n"
    args = _make_args(set_fields=["a=1", "b=hello"])
    with patch("sys.stdin", StringIO(line)):
        run_annotate(args)
    out = capsys.readouterr().out
    record = json.loads(out.strip())
    assert record["a"] == 1
    assert record["b"] == "hello"


def test_run_annotate_skips_blank_lines(capsys):
    lines = "\n" + json.dumps({"msg": "ok"}) + "\n\n"
    args = _make_args(set_fields=["x=1"])
    with patch("sys.stdin", StringIO(lines)):
        run_annotate(args)
    out = capsys.readouterr().out
    records = [json.loads(l) for l in out.strip().splitlines()]
    assert len(records) == 1


def test_run_annotate_invalid_set_spec_returns_error(capsys):
    args = _make_args(set_fields=["no-equals-sign"])
    with patch("sys.stdin", StringIO("")):
        rc = run_annotate(args)
    assert rc == 1
    err = capsys.readouterr().err
    assert "FIELD=VALUE" in err


def test_run_annotate_no_set_fields_passes_through(capsys):
    line = json.dumps({"level": "debug", "msg": "trace"}) + "\n"
    args = _make_args()
    with patch("sys.stdin", StringIO(line)):
        rc = run_annotate(args)
    assert rc == 0
    out = capsys.readouterr().out
    record = json.loads(out.strip())
    assert record["level"] == "debug"
