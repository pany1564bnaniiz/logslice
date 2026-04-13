"""Pipeline: read, filter, and emit log records."""

from typing import Any, Dict, Iterable, Iterator, List, Optional

from logslice.filters import filter_by_field_pattern, filter_by_level, filter_by_time
from logslice.formatter import format_record
from logslice.parser import detect_format, parse_json_line, parse_logfmt_line
from logslice.stats import compute_stats, format_stats


def _iter_records(
    lines: Iterable[str],
    fmt: Optional[str] = None,
) -> Iterator[Dict[str, Any]]:
    """Parse lines into record dicts, auto-detecting format when fmt is None."""
    for line in lines:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        resolved = fmt or detect_format(line)
        if resolved == "json":
            yield parse_json_line(line)
        else:
            yield parse_logfmt_line(line)


def run_pipeline(
    lines: Iterable[str],
    *,
    fmt: Optional[str] = None,
    output_fmt: str = "json",
    level: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    fields: Optional[List[str]] = None,
    show_stats: bool = False,
) -> Iterator[str]:
    """Run the full filter pipeline, yielding formatted output lines.

    When show_stats=True, yields a stats summary block instead of records.
    """
    records = list(_iter_records(lines, fmt=fmt))

    filtered = []
    for record in records:
        if not filter_by_time(record, start=start, end=end):
            continue
        if level and not filter_by_level(record, level):
            continue
        if fields:
            if not all(filter_by_field_pattern(record, f) for f in fields):
                continue
        filtered.append(record)

    if show_stats:
        stats = compute_stats(filtered)
        yield format_stats(stats)
        return

    for record in filtered:
        yield format_record(record, output_fmt)
