"""Sorting utilities for log records."""

from typing import Any


class SorterError(Exception):
    """Raised when sorting fails."""


def _get_sort_key(record: dict, field: str) -> Any:
    """Extract a sort key from a record, returning a default for missing fields."""
    value = record.get(field)
    if value is None:
        # Sort missing values last by returning a tuple that compares high
        return (1, "")
    return (0, str(value))


def sort_records(
    records: list[dict],
    field: str,
    reverse: bool = False,
) -> list[dict]:
    """Sort records by the given field.

    Args:
        records: List of log record dicts.
        field: The field name to sort by.
        reverse: If True, sort in descending order.

    Returns:
        A new sorted list of records.

    Raises:
        SorterError: If field is empty.
    """
    if not field or not field.strip():
        raise SorterError("Sort field must not be empty.")

    return sorted(records, key=lambda r: _get_sort_key(r, field), reverse=reverse)


def sort_by_timestamp(
    records: list[dict],
    timestamp_field: str = "timestamp",
    reverse: bool = False,
) -> list[dict]:
    """Sort records by a timestamp field lexicographically.

    ISO 8601 timestamps sort correctly as strings, so this is safe
    for well-formed log timestamps.

    Args:
        records: List of log record dicts.
        timestamp_field: Name of the timestamp field (default: "timestamp").
        reverse: If True, sort newest-first.

    Returns:
        A new sorted list of records.

    Raises:
        SorterError: If timestamp_field is empty.
    """
    return sort_records(records, field=timestamp_field, reverse=reverse)
