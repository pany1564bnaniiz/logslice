"""logslice.cli_split — CLI integration for the splitter module."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from logslice.formatter import format_record
from logslice.parser import detect_format, parse_json_line, parse_logfmt_line
from logslice.splitter import SplitterError, split_by_field


def add_split_args(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *split* sub-command with *subparsers*."""
    parser = subparsers.add_parser(
        "split",
        help="Split log records by a field value and show per-bucket summaries.",
    )
    parser.add_argument("field", help="Field name to split on.")
    parser.add_argument(
        "--missing-key",
        default="__missing__",
        help="Bucket label for records that lack the field (default: __missing__).",
    )
    parser.add_argument(
        "--format",
        choices=["json", "logfmt", "pretty"],
        default="json",
        help="Output format for individual records (default: json).",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print only a JSON summary of bucket counts instead of records.",
    )


def run_split(args: argparse.Namespace, lines: List[str], out=None) -> None:
    """Execute the split command.

    Args:
        args: Parsed CLI arguments (must include .field, .missing_key,
              .format, .summary).
        lines: Raw log lines to process.
        out: Output stream (defaults to sys.stdout).
    """
    if out is None:
        out = sys.stdout

    records = []
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        fmt = detect_format(raw)
        try:
            if fmt == "json":
                records.append(parse_json_line(raw))
            else:
                records.append(parse_logfmt_line(raw))
        except Exception:
            continue

    try:
        buckets = split_by_field(records, args.field, missing_key=args.missing_key)
    except SplitterError as exc:
        print(f"split error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.summary:
        summary = {bucket: len(recs) for bucket, recs in sorted(buckets.items())}
        out.write(json.dumps(summary) + "\n")
        return

    for bucket, recs in sorted(buckets.items()):
        out.write(f"# bucket: {bucket} ({len(recs)} records)\n")
        for record in recs:
            out.write(format_record(record, fmt=args.format) + "\n")
