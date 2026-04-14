"""Field profiling: compute value distributions and type summaries for log records."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional


class ProfilerError(Exception):
    """Raised when profiling fails."""


def _infer_type(value: Any) -> str:
    """Return a simple type label for a field value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "dict"
    return "unknown"


def profile_field(records: List[Dict[str, Any]], field: str, top_n: int = 10) -> Dict[str, Any]:
    """Return a profile summary for a single field across all records."""
    if not field or not field.strip():
        raise ProfilerError("field name must be a non-empty string")
    if top_n < 1:
        raise ProfilerError("top_n must be at least 1")

    present = 0
    missing = 0
    type_counts: Counter = Counter()
    value_counts: Counter = Counter()

    for record in records:
        if field in record:
            present += 1
            val = record[field]
            type_counts[_infer_type(val)] += 1
            # Only count hashable scalar values
            if isinstance(val, (str, int, float, bool)) or val is None:
                value_counts[str(val)] += 1
        else:
            missing += 1

    total = present + missing
    return {
        "field": field,
        "total": total,
        "present": present,
        "missing": missing,
        "coverage": round(present / total, 4) if total > 0 else 0.0,
        "types": dict(type_counts),
        "top_values": value_counts.most_common(top_n),
    }


def profile_records(records: List[Dict[str, Any]], top_n: int = 10) -> Dict[str, Any]:
    """Return a full profile of all fields found across records."""
    if not records:
        return {"total_records": 0, "fields": {}}

    all_fields: set = set()
    for record in records:
        all_fields.update(record.keys())

    field_profiles = {
        f: profile_field(records, f, top_n=top_n) for f in sorted(all_fields)
    }
    return {
        "total_records": len(records),
        "fields": field_profiles,
    }
