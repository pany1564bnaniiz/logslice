"""CLI sub-command: enrich — add derived fields to log records."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from logslice.enricher import EnricherError, enrich_with_lookup, enrich_with_regex
from logslice.parser import detect_format, parse_json_line, parse_logfmt_line
from logslice.formatter import format_record


def add_enrich_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *enrich* sub-command with *subparsers*."""
    parser = subparsers.add_parser(
        "enrich",
        help="Derive new fields from existing record data.",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="Input log file (default: stdin).",
    )
    parser.add_argument(
        "--regex",
        metavar="SRC:PATTERN:TARGET",
        action="append",
        default=[],
        help="Extract regex group 1 from SRC and store in TARGET.",
    )
    parser.add_argument(
        "--lookup",
        metavar="SRC:JSON_MAP:TARGET",
        action="append",
        default=[],
        help="Map SRC value through JSON_MAP dict and store in TARGET.",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "logfmt", "pretty"],
        default="json",
        help="Output format (default: json).",
    )
    parser.set_defaults(func=run_enrich)


def _parse_regex_spec(spec: str):
    parts = spec.split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"--regex requires SRC:PATTERN:TARGET, got: {spec!r}")
    return parts[0], parts[1], parts[2]


def _parse_lookup_spec(spec: str):
    parts = spec.split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"--lookup requires SRC:JSON_MAP:TARGET, got: {spec!r}")
    src, raw_map, target = parts
    try:
        mapping = json.loads(raw_map)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON map in --lookup: {exc}") from exc
    if not isinstance(mapping, dict):
        raise ValueError("JSON map in --lookup must be a JSON object")
    return src, mapping, target


def run_enrich(args: argparse.Namespace) -> None:
    """Execute the enrich sub-command."""
    fh = open(args.input) if args.input != "-" else sys.stdin  # type: ignore[assignment]
    try:
        for raw in fh:
            raw = raw.rstrip("\n")
            if not raw.strip():
                continue
            fmt = detect_format(raw)
            record = parse_json_line(raw) if fmt == "json" else parse_logfmt_line(raw)
            try:
                for spec in args.regex:
                    src, pattern, target = _parse_regex_spec(spec)
                    record = enrich_with_regex(record, src, pattern, target)
                for spec in args.lookup:
                    src, mapping, target = _parse_lookup_spec(spec)
                    record = enrich_with_lookup(record, src, mapping, target)
            except (EnricherError, ValueError) as exc:
                print(f"[enrich error] {exc}", file=sys.stderr)
                continue
            print(format_record(record, args.output_format))
    finally:
        if args.input != "-":
            fh.close()
