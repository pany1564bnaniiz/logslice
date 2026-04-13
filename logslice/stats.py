"""Statistics and summary reporting for log records."""

from collections import Counter
from typing import Any, Dict, Iterable, List, Optional


class StatsError(Exception):
    """Raised when statistics cannot be computed."""


def compute_stats(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute summary statistics over an iterable of log records.

    Returns a dict with:
      - total: total number of records
      - by_level: counts per log level
      - fields: set of all field names seen
      - time_range: {min, max} ISO timestamps if 'timestamp' present
    """
    total = 0
    level_counts: Counter = Counter()
    field_names: set = set()
    timestamps: List[str] = []

    for record in records:
        if not isinstance(record, dict):
            raise StatsError(f"Expected dict record, got {type(record).__name__}")
        total += 1
        field_names.update(record.keys())

        level = record.get("level") or record.get("severity") or record.get("lvl")
        if level is not None:
            level_counts[str(level).upper()] += 1

        ts = record.get("timestamp") or record.get("time") or record.get("ts")
        if ts is not None:
            timestamps.append(str(ts))

    time_range: Optional[Dict[str, str]] = None
    if timestamps:
        sorted_ts = sorted(timestamps)
        time_range = {"min": sorted_ts[0], "max": sorted_ts[-1]}

    return {
        "total": total,
        "by_level": dict(level_counts),
        "fields": sorted(field_names),
        "time_range": time_range,
    }


def format_stats(stats: Dict[str, Any]) -> str:
    """Format a stats dict as a human-readable summary string."""
    lines = [
        f"Total records : {stats['total']}",
    ]

    if stats["by_level"]:
        lines.append("By level      :")
        for lvl, count in sorted(stats["by_level"].items()):
            lines.append(f"  {lvl:<12} {count}")
    else:
        lines.append("By level      : (no level field found)")

    if stats["time_range"]:
        lines.append(f"Time range    : {stats['time_range']['min']}  ->  {stats['time_range']['max']}")
    else:
        lines.append("Time range    : (no timestamp field found)")

    lines.append(f"Fields seen   : {', '.join(stats['fields'])}")
    return "\n".join(lines)
