"""Field enrichment: derive or inject new fields based on existing record data."""

from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional


class EnricherError(Exception):
    """Raised when an enrichment operation fails."""


def enrich_with_regex(
    record: Dict[str, Any],
    source_field: str,
    pattern: str,
    target_field: str,
    group: int = 1,
    default: Optional[str] = None,
) -> Dict[str, Any]:
    """Extract a regex group from *source_field* and store it in *target_field*."""
    if not source_field or not source_field.strip():
        raise EnricherError("source_field must be a non-empty string")
    if not target_field or not target_field.strip():
        raise EnricherError("target_field must be a non-empty string")
    if not pattern:
        raise EnricherError("pattern must be a non-empty string")

    value = record.get(source_field)
    result = {**record}
    if value is None:
        result[target_field] = default
        return result

    match = re.search(pattern, str(value))
    result[target_field] = match.group(group) if match else default
    return result


def enrich_with_lookup(
    record: Dict[str, Any],
    source_field: str,
    lookup: Dict[str, Any],
    target_field: str,
    default: Optional[Any] = None,
) -> Dict[str, Any]:
    """Map *source_field* value through *lookup* dict and store in *target_field*."""
    if not source_field or not source_field.strip():
        raise EnricherError("source_field must be a non-empty string")
    if not target_field or not target_field.strip():
        raise EnricherError("target_field must be a non-empty string")
    if not isinstance(lookup, dict):
        raise EnricherError("lookup must be a dict")

    key = record.get(source_field)
    result = {**record}
    result[target_field] = lookup.get(str(key), default) if key is not None else default
    return result


def enrich_with_callable(
    record: Dict[str, Any],
    target_field: str,
    fn: Callable[[Dict[str, Any]], Any],
) -> Dict[str, Any]:
    """Call *fn* with the record and store the return value in *target_field*."""
    if not target_field or not target_field.strip():
        raise EnricherError("target_field must be a non-empty string")
    if not callable(fn):
        raise EnricherError("fn must be callable")

    result = {**record}
    try:
        result[target_field] = fn(record)
    except Exception as exc:  # pragma: no cover
        raise EnricherError(f"enrichment callable raised: {exc}") from exc
    return result


def apply_enrichments(
    records: List[Dict[str, Any]],
    enrichments: List[Callable[[Dict[str, Any]], Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Apply a sequence of enrichment callables to every record."""
    result = []
    for record in records:
        for enrich in enrichments:
            record = enrich(record)
        result.append(record)
    return result
