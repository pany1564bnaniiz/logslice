"""CLI sub-command: normalize — apply field normalizations to log records."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from logslice.normalizer import NormalizerError, apply_normalizations
from logslice.parser import detect_format, parse_json_line, parse_logfmt_line
from logslice.formatter import format_record


def add_normalize_args(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *normalize* sub-command with *subparsers*."""
    p = subparsers.add_parser(
        "normalize",
        help="Normalize field values (lowercase, uppercase, strip whitespace).",
    )
    p.add_argument(
        "--lowercase",
        metavar="FIELD",
        action="append",
        default=[],
        help="Lowercase the value of FIELD.",
    )
    p.add_argument(
        "--uppercase",
        metavar="FIELD",
        action="append",
        default=[],
        help="Uppercase the value of FIELD.",
    )
    p.add_argument(
        "--strip",
        metavar="FIELD",
        action="append",
        default=[],
        help="Strip whitespace from the value of FIELD.",
    )
    p.add_argument(
        "--output-format",
        choices=["json", "logfmt", "pretty"],
        default="json",
        help="Output format (default: json).",
    )
    p.set_defaults(func=run_normalize)


def run_normalize(args: argparse.Namespace, input_lines: List[str] | None = None) -> str:
    """Execute the normalize sub-command and return formatted output."""
    lines = input_lines if input_lines is not None else sys.stdin.read().splitlines()

    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        fmt = detect_format(line)
        if fmt == "json":
            records.append(parse_json_line(line))
        else:
            records.append(parse_logfmt_line(line))

    normalizations = []
    for field in args.lowercase:
        normalizations.append({"type": "lowercase", "field": field})
    for field in args.uppercase:
        normalizations.append({"type": "uppercase", "field": field})
    for field in args.strip:
        normalizations.append({"type": "strip", "field": field})

    try:
        normalized = apply_normalizations(records, normalizations)
    except NormalizerError as exc:
        print(f"normalize error: {exc}", file=sys.stderr)
        sys.exit(1)

    return "\n".join(format_record(r, args.output_format) for r in normalized)
