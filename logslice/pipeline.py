"""Pipeline orchestration for logslice: parse, filter, transform, format."""

from typing import IO, Iterator

from logslice.filters import filter_by_field_pattern, filter_by_level, filter_by_time
from logslice.formatter import format_record
from logslice.parser import detect_format, parse_json_line, parse_logfmt_line
from logslice.transform import apply_transforms


def _iter_records(stream: IO[str], fmt: str | None = None) -> Iterator[dict]:
    """Yield parsed records from a text stream.

    Auto-detects format from the first non-empty line when fmt is None.
    """
    parser = None
    for raw in stream:
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        if parser is None:
            detected = fmt or detect_format(line)
            parser = parse_json_line if detected == "json" else parse_logfmt_line
        yield parser(line)


def run_pipeline(
    stream: IO[str],
    *,
    fmt: str | None = None,
    output_fmt: str = "json",
    level: str | None = None,
    start: str | None = None,
    end: str | None = None,
    field_pattern: tuple[str, str] | None = None,
    transforms: list[dict] | None = None,
    output: IO[str],
) -> int:
    """Run the full logslice pipeline and write results to *output*.

    Returns the number of records written.
    """
    count = 0
    for record in _iter_records(stream, fmt):
        if not filter_by_time(record, start=start, end=end):
            continue
        if level and not filter_by_level(record, level):
            continue
        if field_pattern and not filter_by_field_pattern(record, *field_pattern):
            continue
        if transforms:
            record = apply_transforms(record, transforms)
        output.write(format_record(record, output_fmt))
        output.write("\n")
        count += 1
    return count
