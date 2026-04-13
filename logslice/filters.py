"""Filtering logic for log entries by time range, level, and field patterns."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional


class FilterError(Exception):
    """Raised when a filter cannot be applied due to invalid input."""


def _parse_timestamp(value: Any) -> Optional[datetime]:
    """Attempt to parse a timestamp value into a datetime object."""
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=timezone.utc)
    if isinstance(value, str):
        for fmt in (
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                dt = datetime.strptime(value.rstrip("Z") + "+00:00" if value.endswith("Z") else value, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
    return None


def filter_by_time(
    entry: dict[str, Any],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    time_field: str = "time",
) -> bool:
    """Return True if the entry falls within [start, end] (inclusive)."""
    raw = entry.get(time_field) or entry.get("timestamp") or entry.get("ts")
    if raw is None:
        return True  # no timestamp field — don't filter out

    ts = _parse_timestamp(raw)
    if ts is None:
        return True

    if start and ts < start:
        return False
    if end and ts > end:
        return False
    return True


def filter_by_level(
    entry: dict[str, Any],
    levels: Optional[list[str]] = None,
    level_field: str = "level",
) -> bool:
    """Return True if the entry's log level is in the allowed levels list."""
    if not levels:
        return True

    raw = entry.get(level_field) or entry.get("lvl") or entry.get("severity")
    if raw is None:
        return False

    return str(raw).lower() in {lvl.lower() for lvl in levels}


def filter_by_field_pattern(
    entry: dict[str, Any],
    field: str,
    pattern: str,
) -> bool:
    """Return True if the entry's field value matches the given regex pattern."""
    value = entry.get(field)
    if value is None:
        return False
    try:
        return bool(re.search(pattern, str(value)))
    except re.error as exc:
        raise FilterError(f"Invalid regex pattern {pattern!r}: {exc}") from exc
