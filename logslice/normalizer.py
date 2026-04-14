"""Field normalization utilities for log records."""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


class NormalizerError(Exception):
    """Raised when a normalization operation fails."""


def normalize_field(
    record: Dict[str, Any],
    field: str,
    transform: Callable[[Any], Any],
) -> Dict[str, Any]:
    """Apply *transform* to the value of *field* in *record*.

    Returns a new record; does not mutate the original.
    Raises NormalizerError if *field* is empty or the transform raises.
    """
    if not field or not field.strip():
        raise NormalizerError("field name must not be empty")
    result = dict(record)
    if field in result:
        try:
            result[field] = transform(result[field])
        except Exception as exc:  # noqa: BLE001
            raise NormalizerError(
                f"transform failed on field '{field}': {exc}"
            ) from exc
    return result


def lowercase_field(record: Dict[str, Any], field: str) -> Dict[str, Any]:
    """Lowercase the string value of *field*."""
    def _lower(v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError(f"expected str, got {type(v).__name__}")
        return v.lower()

    return normalize_field(record, field, _lower)


def uppercase_field(record: Dict[str, Any], field: str) -> Dict[str, Any]:
    """Uppercase the string value of *field*."""
    def _upper(v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError(f"expected str, got {type(v).__name__}")
        return v.upper()

    return normalize_field(record, field, _upper)


def strip_field(record: Dict[str, Any], field: str) -> Dict[str, Any]:
    """Strip leading/trailing whitespace from the string value of *field*."""
    def _strip(v: Any) -> str:
        if not isinstance(v, str):
            raise TypeError(f"expected str, got {type(v).__name__}")
        return v.strip()

    return normalize_field(record, field, _strip)


def apply_normalizations(
    records: List[Dict[str, Any]],
    normalizations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Apply a sequence of normalization specs to every record.

    Each spec is a dict with keys:
      - ``type``: one of ``"lowercase"``, ``"uppercase"``, ``"strip"``, ``"custom"``
      - ``field``: the field name to normalize
      - ``transform`` (only for ``"custom"``): a callable
    """
    _dispatch: Dict[str, Callable] = {
        "lowercase": lowercase_field,
        "uppercase": uppercase_field,
        "strip": strip_field,
    }
    result = list(records)
    for spec in normalizations:
        ntype = spec.get("type", "")
        field = spec.get("field", "")
        if ntype == "custom":
            fn: Callable = spec["transform"]
            result = [normalize_field(r, field, fn) for r in result]
        elif ntype in _dispatch:
            op = _dispatch[ntype]
            result = [op(r, field) for r in result]
        else:
            raise NormalizerError(f"unknown normalization type: '{ntype}'")
    return result
