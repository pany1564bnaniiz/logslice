"""Merge multiple streams of log records, optionally sorted by timestamp."""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator, List

from logslice.parser import parse_json_line, parse_logfmt_line, detect_format, LogParseError


class MergerError(Exception):
    """Raised when merging fails."""


def merge_sorted(
    streams: List[Iterable[dict]],
    timestamp_field: str = "timestamp",
) -> Iterator[dict]:
    """Merge multiple pre-sorted record streams into one sorted stream.

    Uses a min-heap for efficiency.  Records without the timestamp field
    are appended at the end in their original order.
    """
    if not timestamp_field or not timestamp_field.strip():
        raise MergerError("timestamp_field must be a non-empty string")

    if not streams:
        return

    # Wrap each stream in an iterator tagged with its index to break ties
    def _tagged(idx: int, it: Iterable[dict]):
        for record in it:
            yield record

    iters = [iter(_tagged(i, s)) for i, s in enumerate(streams)]
    heap: list = []
    late: list = []

    # Seed the heap with the first record from each stream
    for stream_idx, it in enumerate(iters):
        try:
            record = next(it)
            ts = record.get(timestamp_field)
            if ts is not None:
                heapq.heappush(heap, (str(ts), stream_idx, record, it))
            else:
                late.append(record)
        except StopIteration:
            pass

    while heap:
        ts_val, stream_idx, record, it = heapq.heappop(heap)
        yield record
        try:
            nxt = next(it)
            nts = nxt.get(timestamp_field)
            if nts is not None:
                heapq.heappush(heap, (str(nts), stream_idx, nxt, it))
            else:
                late.append(nxt)
        except StopIteration:
            pass

    yield from late


def merge_records(streams: List[Iterable[dict]]) -> Iterator[dict]:
    """Merge multiple record streams in round-robin order (no sorting)."""
    if not streams:
        return
    iters = [iter(s) for s in streams]
    exhausted = [False] * len(iters)
    while not all(exhausted):
        for i, it in enumerate(iters):
            if exhausted[i]:
                continue
            try:
                yield next(it)
            except StopIteration:
                exhausted[i] = True


def merge_files(
    paths: List[str],
    sort: bool = True,
    timestamp_field: str = "timestamp",
) -> Iterator[dict]:
    """Parse and merge log files from disk."""
    if not paths:
        raise MergerError("At least one file path is required")

    def _iter_file(path: str) -> Iterator[dict]:
        with open(path, "r", encoding="utf-8") as fh:
            lines = [l for l in fh if l.strip()]
        if not lines:
            return
        fmt = detect_format(lines[0])
        parser = parse_json_line if fmt == "json" else parse_logfmt_line
        for line in lines:
            try:
                yield parser(line)
            except LogParseError:
                pass

    streams = [list(_iter_file(p)) for p in paths]
    if sort:
        yield from merge_sorted(streams, timestamp_field=timestamp_field)
    else:
        yield from merge_records(streams)
