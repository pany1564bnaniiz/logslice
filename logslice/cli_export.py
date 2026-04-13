"""CLI helpers for the --export flag in logslice.

This module extends the main CLI with export-related argument parsing
and wires the exporter into the pipeline output step.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Dict, Any, Optional

from logslice.exporter import export_records, ExportError

EXPORT_FORMATS = ("jsonl", "csv", "tsv")


def add_export_args(parser: argparse.ArgumentParser) -> None:
    """Attach export-related arguments to an existing ArgumentParser."""
    group = parser.add_argument_group("export options")
    group.add_argument(
        "--export-format",
        choices=EXPORT_FORMATS,
        default=None,
        metavar="FORMAT",
        help=f"Export output format. One of: {', '.join(EXPORT_FORMATS)}",
    )
    group.add_argument(
        "--export-fields",
        nargs="+",
        default=None,
        metavar="FIELD",
        help="Ordered list of fields to include in CSV/TSV export.",
    )
    group.add_argument(
        "--export-output",
        default=None,
        metavar="FILE",
        help="Write exported output to FILE instead of stdout.",
    )


def run_export(
    records: List[Dict[str, Any]],
    fmt: str,
    fieldnames: Optional[List[str]] = None,
    output_path: Optional[str] = None,
) -> None:
    """Serialize *records* in *fmt* and write to *output_path* or stdout.

    Raises SystemExit on error so it integrates cleanly with CLI main().
    """
    try:
        content = export_records(records, fmt, fieldnames=fieldnames)
    except ExportError as exc:
        print(f"logslice export error: {exc}", file=sys.stderr)
        sys.exit(1)

    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8") as fh:
                fh.write(content)
                if content and not content.endswith("\n"):
                    fh.write("\n")
        except OSError as exc:
            print(f"logslice export error: cannot write to '{output_path}': {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(content, end="" if content.endswith("\n") else "\n")
