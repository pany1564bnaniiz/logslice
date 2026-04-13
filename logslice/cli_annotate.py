"""CLI helpers for the annotate sub-command."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from logslice.annotator import AnnotatorError, apply_annotations
from logslice.parser import LogParseError, detect_format, parse_json_line, parse_logfmt_line
from logslice.formatter import format_record


def add_annotate_args(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *annotate* sub-command on *subparsers*."""
    parser = subparsers.add_parser(
        "annotate",
        help="Add static field annotations to every log record.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Input log file (default: stdin).",
    )
    parser.add_argument(
        "--set",
        dest="set_fields",
        metavar="FIELD=VALUE",
        action="append",
        default=[],
        help="Add or overwrite a field with a static value (repeatable).",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "logfmt", "pretty"],
        default="json",
        help="Output format (default: json).",
    )


def _parse_set_fields(set_fields: List[str]) -> List[dict]:
    """Convert ``FIELD=VALUE`` strings into annotation spec dicts."""
    specs = []
    for item in set_fields:
        if "=" not in item:
            raise AnnotatorError(f"--set value must be in FIELD=VALUE format, got: {item!r}")
        field, _, value = item.partition("=")
        field = field.strip()
        if not field:
            raise AnnotatorError(f"field name is empty in --set spec: {item!r}")
        # Attempt JSON decode so numbers/booleans/null work; fall back to str.
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            decoded = value
        specs.append({"field": field, "value": decoded, "overwrite": True})
    return specs


def run_annotate(args: argparse.Namespace) -> int:
    """Execute the annotate sub-command.  Returns an exit code."""
    try:
        specs = _parse_set_fields(args.set_fields)
    except AnnotatorError as exc:
        print(f"logslice annotate: {exc}", file=sys.stderr)
        return 1

    src = open(args.input) if args.input != "-" else sys.stdin  # noqa: SIM115
    try:
        records = []
        for line in src:
            line = line.strip()
            if not line:
                continue
            fmt = detect_format(line)
            try:
                if fmt == "json":
                    records.append(parse_json_line(line))
                else:
                    records.append(parse_logfmt_line(line))
            except LogParseError:
                print(f"logslice annotate: skipping malformed line: {line!r}", file=sys.stderr)
    finally:
        if args.input != "-":
            src.close()

    try:
        annotated = apply_annotations(records, specs)
    except AnnotatorError as exc:
        print(f"logslice annotate: {exc}", file=sys.stderr)
        return 1

    for record in annotated:
        print(format_record(record, args.output_format))

    return 0
