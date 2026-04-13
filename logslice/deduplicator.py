"""Record deduplication utilities for logslice."""

from typing import Any, Dict, FrozenSet, Iterable, Iterator, List, Optional, Tuple


class DeduplicatorError(Exception):
    """Raised when deduplication configuration is invalid."""


def _record_key(record: Dict[str, Any], fields: Optional[List[str]]) -> Tuple:
    """Build a hashable key from a record based on selected fields."""
    if fields is None:
        return tuple(sorted((k, str(v)) for k, v in record.items()))
    return tuple((f, str(record.get(f))) for f in sorted(fields))


def deduplicate(
    records: Iterable[Dict[str, Any]],
    fields: Optional[List[str]] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield records, skipping exact duplicates.

    Args:
        records: Iterable of parsed log records.
        fields: Optional list of field names to use as the uniqueness key.
                If None, all fields are used.

    Yields:
        Unique records in original order.

    Raises:
        DeduplicatorError: If fields list is provided but empty.
    """
    if fields is not None and len(fields) == 0:
        raise DeduplicatorError("fields list must not be empty when provided")

    seen: set = set()
    for record in records:
        key = _record_key(record, fields)
        if key not in seen:
            seen.add(key)
            yield record


def count_duplicates(
    records: Iterable[Dict[str, Any]],
    fields: Optional[List[str]] = None,
) -> int:
    """Return the number of duplicate records that would be removed.

    Args:
        records: Iterable of parsed log records.
        fields: Optional list of field names to use as the uniqueness key.

    Returns:
        Count of records that are duplicates (total - unique).

    Raises:
        DeduplicatorError: If fields list is provided but empty.
    """
    if fields is not None and len(fields) == 0:
        raise DeduplicatorError("fields list must not be empty when provided")

    seen: set = set()
    total = 0
    dupes = 0
    for record in records:
        total += 1
        key = _record_key(record, fields)
        if key in seen:
            dupes += 1
        else:
            seen.add(key)
    return dupes
