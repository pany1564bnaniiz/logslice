"""Field value truncation utilities for logslice."""

from typing import Any


class TruncatorError(Exception):
    """Raised when truncation parameters are invalid."""


def truncate_field(
    record: dict[str, Any],
    field: str,
    max_length: int,
    ellipsis: str = "...",
) -> dict[str, Any]:
    """Return a copy of record with the named field truncated to max_length.

    If the field value is not a string it is left unchanged.
    The ellipsis suffix is appended only when the value is actually shortened.
    """
    if not field:
        raise TruncatorError("field name must not be empty")
    if max_length < 1:
        raise TruncatorError("max_length must be at least 1")
    if field not in record:
        raise TruncatorError(f"field {field!r} not found in record")

    result = dict(record)
    value = result[field]
    if isinstance(value, str) and len(value) > max_length:
        cut = max(0, max_length - len(ellipsis))
        result[field] = value[:cut] + ellipsis
    return result


def truncate_all_fields(
    record: dict[str, Any],
    max_length: int,
    ellipsis: str = "...",
    skip_fields: list[str] | None = None,
) -> dict[str, Any]:
    """Return a copy of record with every string field truncated to max_length.

    Fields listed in *skip_fields* are left unchanged.
    """
    if max_length < 1:
        raise TruncatorError("max_length must be at least 1")

    skip = set(skip_fields or [])
    result = dict(record)
    for key, value in result.items():
        if key in skip:
            continue
        if isinstance(value, str) and len(value) > max_length:
            cut = max(0, max_length - len(ellipsis))
            result[key] = value[:cut] + ellipsis
    return result


def apply_truncations(
    records: list[dict[str, Any]],
    field: str | None = None,
    max_length: int = 80,
    ellipsis: str = "...",
    skip_fields: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Apply truncation to a list of records.

    If *field* is given, only that field is truncated; otherwise every string
    field is truncated (honouring *skip_fields*).
    """
    if field:
        return [truncate_field(r, field, max_length, ellipsis) for r in records]
    return [
        truncate_all_fields(r, max_length, ellipsis, skip_fields) for r in records
    ]
