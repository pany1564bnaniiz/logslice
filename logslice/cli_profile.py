"""CLI subcommand: profile — show field distributions for log records."""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace
from typing import List

from logslice.parser import detect_format, parse_json_line, parse_logfmt_line
from logslice.profiler import ProfilerError, profile_field, profile_records


def add_profile_args(subparsers) -> None:
    """Register the 'profile' subcommand."""
    p: ArgumentParser = subparsers.add_parser(
        "profile", help="Profile field distributions in log records"
    )
    p.add_argument("input", nargs="?", default="-", help="Input file (default: stdin)")
    p.add_argument(
        "--field", "-f", default=None, help="Profile a single field only"
    )
    p.add_argument(
        "--top", "-n", type=int, default=10, help="Number of top values to show (default: 10)"
    )
    p.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    p.set_defaults(func=run_profile)


def _read_records(source: str) -> List[dict]:
    if source == "-":
        lines = sys.stdin.read().splitlines()
    else:
        with open(source, "r", encoding="utf-8") as fh:
            lines = fh.read().splitlines()

    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        fmt = detect_format(line)
        try:
            if fmt == "json":
                records.append(parse_json_line(line))
            else:
                records.append(parse_logfmt_line(line))
        except Exception:
            continue
    return records


def _render_text(profile: dict) -> str:
    lines = []
    if "fields" in profile:
        lines.append(f"Total records: {profile['total_records']}")
        for fname, fp in profile["fields"].items():
            lines.append(_render_field_text(fp))
    else:
        lines.append(_render_field_text(profile))
    return "\n".join(lines)


def _render_field_text(fp: dict) -> str:
    parts = [
        f"Field: {fp['field']}",
        f"  present={fp['present']} missing={fp['missing']} coverage={fp['coverage']:.2%}",
        f"  types: {fp['types']}",
        f"  top values: {fp['top_values']}",
    ]
    return "\n".join(parts)


def run_profile(args: Namespace) -> None:
    records = _read_records(args.input)
    top_n = args.top

    try:
        if args.field:
            result = profile_field(records, args.field, top_n=top_n)
        else:
            result = profile_records(records, top_n=top_n)
    except ProfilerError as exc:
        print(f"profile error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(_render_text(result))
