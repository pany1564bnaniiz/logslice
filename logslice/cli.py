"""Command-line interface for logslice."""

import argparse
import sys
from typing import List, Optional

from logslice.formatter import SUPPORTED_FORMATS
from logslice.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Filter and slice structured log files by time, level, or field patterns.",
    )
    p.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Log file to read (default: stdin).",
    )
    p.add_argument("--start", metavar="TIMESTAMP", help="Include records at or after this time.")
    p.add_argument("--end", metavar="TIMESTAMP", help="Include records at or before this time.")
    p.add_argument("--level", metavar="LEVEL", help="Include only records at this log level.")
    p.add_argument(
        "--field",
        metavar="KEY=PATTERN",
        dest="field_pattern",
        help="Include only records where KEY matches PATTERN (regex).",
    )
    p.add_argument(
        "--fmt",
        choices=("json", "logfmt"),
        default=None,
        help="Force input format (default: auto-detect).",
    )
    p.add_argument(
        "--out",
        choices=SUPPORTED_FORMATS,
        default="json",
        dest="out_fmt",
        help="Output format (default: json).",
    )
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.file == "-":
            stream = sys.stdin
            count = run_pipeline(
                stream,
                sys.stdout,
                fmt=args.fmt,
                out_fmt=args.out_fmt,
                start=args.start,
                end=args.end,
                level=args.level,
                field_pattern=args.field_pattern,
            )
        else:
            with open(args.file, "r", encoding="utf-8") as fh:
                count = run_pipeline(
                    fh,
                    sys.stdout,
                    fmt=args.fmt,
                    out_fmt=args.out_fmt,
                    start=args.start,
                    end=args.end,
                    level=args.level,
                    field_pattern=args.field_pattern,
                )
    except FileNotFoundError:
        print(f"logslice: file not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"logslice: error: {exc}", file=sys.stderr)
        return 1

    print(f"# {count} record(s) matched.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
