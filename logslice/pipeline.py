"""Orchestrates parsing, filtering, and formatting of log lines."""

from typing import IO, Iterator, Optional

from logslice.filters import filter_by_field_pattern, filter_by_level, filter_by_time
from logslice.formatter import format_record
from logslice.parser import LogParseError, detect_format, parse_json_line, parse_logfmt_line


def _iter_records(stream: IO[str], fmt: Optional[str] = None) -> Iterator[dict]:
    """Yield parsed records from a line-oriented log stream."""
    detected: Optional[str] = fmt
    for raw_line in stream:
        line = raw_line.rstrip("\n")
        if not line.strip():
            continue
        if detected is None:
            detected = detect_format(line)
        try:
            if detected == "json":
                yield parse_json_line(line)
            else:
                yield parse_logfmt_line(line)
        except LogParseError:
            continue


def run_pipeline(
    stream: IO[str],
    output: IO[str],
    *,
    fmt: Optional[str] = None,
    out_fmt: str = "json",
    start: Optional[str] = None,
    end: Optional[str] = None,
    level: Optional[str] = None,
    field_pattern: Optional[str] = None,
) -> int:
    """Filter and format log records from *stream* into *output*.

    Returns the number of records written.
    """
    written = 0
    for record in _iter_records(stream, fmt=fmt):
        if not filter_by_time(record, start=start, end=end):
            continue
        if level and not filter_by_level(record, level=level):
            continue
        if field_pattern and not filter_by_field_pattern(record, pattern=field_pattern):
            continue
        output.write(format_record(record, fmt=out_fmt))
        output.write("\n")
        written += 1
    return written
