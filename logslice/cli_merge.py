"""CLI helpers for the merge sub-command."""

from __future__ import annotations

import argparse
import sys
from typing import List

from logslice.merger import merge_files, MergerError
from logslice.formatter import format_record


def add_merge_args(parser: argparse.ArgumentParser) -> None:
    """Register merge-specific arguments on *parser*."""
    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="Two or more log files to merge.",
    )
    parser.add_argument(
        "--no-sort",
        action="store_true",
        default=False,
        help="Merge in round-robin order instead of sorting by timestamp.",
    )
    parser.add_argument(
        "--timestamp-field",
        default="timestamp",
        metavar="FIELD",
        help="Record field used for sorting (default: timestamp).",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "logfmt", "pretty"],
        default="json",
        help="Output format for merged records (default: json).",
    )


def run_merge(args: argparse.Namespace, out=None) -> int:
    """Execute the merge command.  Returns an exit code."""
    if out is None:
        out = sys.stdout

    if len(args.files) < 2:
        print("error: merge requires at least two input files", file=sys.stderr)
        return 1

    try:
        records = merge_files(
            args.files,
            sort=not args.no_sort,
            timestamp_field=args.timestamp_field,
        )
        for record in records:
            out.write(format_record(record, fmt=args.output_format) + "\n")
    except MergerError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error reading file: {exc}", file=sys.stderr)
        return 1

    return 0
