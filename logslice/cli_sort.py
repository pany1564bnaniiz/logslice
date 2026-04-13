"""CLI helpers for the sort subcommand."""

import argparse
import json
import sys

from logslice.sorter import SorterError, sort_records, sort_by_timestamp


def add_sort_args(parser: argparse.ArgumentParser) -> None:
    """Register sort-related arguments onto *parser*."""
    parser.add_argument(
        "--sort-by",
        metavar="FIELD",
        default=None,
        help="Field to sort records by (default: timestamp).",
    )
    parser.add_argument(
        "--sort-desc",
        action="store_true",
        default=False,
        help="Sort in descending order (newest / highest first).",
    )
    parser.add_argument(
        "--sort-timestamp-field",
        metavar="FIELD",
        default="timestamp",
        help="Timestamp field used when --sort-by is not specified (default: timestamp).",
    )


def run_sort(args: argparse.Namespace, records: list[dict]) -> list[dict]:
    """Apply sorting to *records* according to parsed CLI *args*.

    Returns the sorted list.  Writes an error message to stderr and
    exits with code 1 on failure.
    """
    try:
        if args.sort_by:
            return sort_records(records, field=args.sort_by, reverse=args.sort_desc)
        return sort_by_timestamp(
            records,
            timestamp_field=args.sort_timestamp_field,
            reverse=args.sort_desc,
        )
    except SorterError as exc:
        print(f"sort error: {exc}", file=sys.stderr)
        sys.exit(1)
