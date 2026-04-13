"""Pipeline orchestration for logslice.

Reads lines from an input stream, parses them, applies filters and optional
sampling, then formats and writes the results.
"""

from __future__ import annotations

from typing import IO, Iterable, Iterator

from logslice.filters import filter_by_field_pattern, filter_by_level, filter_by_time
from logslice.formatter import format_record
from logslice.parser import detect_format, parse_json_line, parse_logfmt_line
from logslice.sampler import apply_sampler


def _iter_records(lines: Iterable[str], fmt: str) -> Iterator[dict]:
    """Parse *lines* according to *fmt*, silently skipping unparseable lines."""
    parse = parse_json_line if fmt == "json" else parse_logfmt_line
    for line in lines:
        line = line.rstrip("\n")
        if not line.strip():
            continue
        try:
            yield parse(line)
        except Exception:
            continue


def run_pipeline(
    input_stream: IO[str],
    output_stream: IO[str],
    *,
    fmt: str | None = None,
    output_fmt: str = "json",
    start: str | None = None,
    end: str | None = None,
    level: str | None = None,
    field_pattern: str | None = None,
    nth: int | None = None,
    sample_rate: float | None = None,
    sample_seed: int | None = None,
) -> int:
    """Run the full logslice pipeline and return the number of records written.

    Args:
        input_stream: Readable text stream of log lines.
        output_stream: Writable text stream for formatted output.
        fmt: Input format (``'json'`` or ``'logfmt'``).  Auto-detected when
            ``None``.
        output_fmt: Output format passed to :func:`format_record`.
        start: ISO-8601 / Unix timestamp lower bound (inclusive).
        end: ISO-8601 / Unix timestamp upper bound (inclusive).
        level: Minimum log level to include.
        field_pattern: ``field=pattern`` filter expression.
        nth: Keep every *n*-th record.
        sample_rate: Keep each record with this probability (0.0–1.0).
        sample_seed: RNG seed for reproducible random sampling.

    Returns:
        Number of records written to *output_stream*.
    """
    lines = list(input_stream)

    resolved_fmt = fmt or detect_format(lines)

    records: Iterable[dict] = _iter_records(lines, resolved_fmt)

    if start is not None or end is not None:
        records = (r for r in records if filter_by_time(r, start=start, end=end))

    if level is not None:
        records = (r for r in records if filter_by_level(r, level))

    if field_pattern is not None:
        records = (
            r for r in records if filter_by_field_pattern(r, field_pattern)
        )

    records = apply_sampler(records, nth=nth, rate=sample_rate, seed=sample_seed)

    count = 0
    for record in records:
        output_stream.write(format_record(record, output_fmt) + "\n")
        count += 1

    return count
