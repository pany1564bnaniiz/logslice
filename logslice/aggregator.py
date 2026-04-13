"""Field aggregation utilities for logslice."""

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional


class AggregatorError(Exception):
    """Raised when aggregation fails."""


def group_by(records: Iterable[Dict[str, Any]], field: str) -> Dict[str, List[Dict[str, Any]]]:
    """Group records by the value of a given field.

    Args:
        records: Iterable of parsed log records.
        field: The field name to group by.

    Returns:
        A dict mapping field values to lists of matching records.

    Raises:
        AggregatorError: If field is empty.
    """
    if not field:
        raise AggregatorError("group_by field must not be empty")

    groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        key = str(record.get(field, "__missing__"))
        groups[key].append(record)
    return dict(groups)


def count_by(records: Iterable[Dict[str, Any]], field: str) -> Dict[str, int]:
    """Count records grouped by the value of a given field.

    Args:
        records: Iterable of parsed log records.
        field: The field name to count by.

    Returns:
        A dict mapping field values to occurrence counts.

    Raises:
        AggregatorError: If field is empty.
    """
    if not field:
        raise AggregatorError("count_by field must not be empty")

    counts: Dict[str, int] = defaultdict(int)
    for record in records:
        key = str(record.get(field, "__missing__"))
        counts[key] += 1
    return dict(counts)


def top_values(
    records: Iterable[Dict[str, Any]], field: str, n: int = 10
) -> List[tuple]:
    """Return the top N most frequent values for a field.

    Args:
        records: Iterable of parsed log records.
        field: The field name to analyse.
        n: Number of top entries to return.

    Returns:
        A list of (value, count) tuples sorted by count descending.

    Raises:
        AggregatorError: If field is empty or n < 1.
    """
    if not field:
        raise AggregatorError("top_values field must not be empty")
    if n < 1:
        raise AggregatorError(f"n must be >= 1, got {n}")

    counts = count_by(records, field)
    sorted_items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return sorted_items[:n]
