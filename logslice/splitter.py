"""logslice.splitter — Split records into multiple buckets by field value."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional


class SplitterError(Exception):
    """Raised when splitting fails."""


def split_by_field(
    records: Iterable[dict],
    field: str,
    missing_key: str = "__missing__",
) -> Dict[str, List[dict]]:
    """Group records into buckets keyed by the value of *field*.

    Args:
        records: Iterable of log record dicts.
        field: Field name to split on.
        missing_key: Bucket name used when a record lacks *field*.

    Returns:
        A dict mapping each distinct field value to the list of matching records.

    Raises:
        SplitterError: If *field* is empty or whitespace.
    """
    if not field or not field.strip():
        raise SplitterError("field must be a non-empty string")

    buckets: Dict[str, List[dict]] = defaultdict(list)
    for record in records:
        key = record.get(field)
        bucket_key = str(key) if key is not None else missing_key
        buckets[bucket_key].append(record)
    return dict(buckets)


def split_by_predicate(
    records: Iterable[dict],
    predicates: Dict[str, object],
    default_bucket: str = "other",
) -> Dict[str, List[dict]]:
    """Route each record into the first bucket whose callable predicate returns True.

    Args:
        records: Iterable of log record dicts.
        predicates: Ordered mapping of bucket_name -> callable(record) -> bool.
        default_bucket: Bucket for records that match no predicate.

    Returns:
        A dict mapping bucket names to lists of records.

    Raises:
        SplitterError: If *predicates* is empty.
    """
    if not predicates:
        raise SplitterError("predicates must not be empty")

    buckets: Dict[str, List[dict]] = defaultdict(list)
    for record in records:
        matched = False
        for bucket_name, predicate in predicates.items():
            if callable(predicate) and predicate(record):
                buckets[bucket_name].append(record)
                matched = True
                break
        if not matched:
            buckets[default_bucket].append(record)
    return dict(buckets)
