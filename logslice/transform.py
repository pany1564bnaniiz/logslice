"""Field transformation utilities for logslice records."""

from typing import Any


class TransformError(Exception):
    """Raised when a transformation cannot be applied."""


def rename_field(record: dict, old_key: str, new_key: str) -> dict:
    """Return a copy of record with old_key renamed to new_key.

    Raises TransformError if old_key does not exist in record.
    """
    if old_key not in record:
        raise TransformError(f"Field '{old_key}' not found in record")
    if not new_key or not isinstance(new_key, str):
        raise TransformError("new_key must be a non-empty string")
    result = dict(record)
    result[new_key] = result.pop(old_key)
    return result


def drop_fields(record: dict, fields: list[str]) -> dict:
    """Return a copy of record with specified fields removed."""
    if not fields:
        return dict(record)
    return {k: v for k, v in record.items() if k not in fields}


def keep_fields(record: dict, fields: list[str]) -> dict:
    """Return a copy of record containing only the specified fields.

    Raises TransformError if fields list is empty.
    """
    if not fields:
        raise TransformError("fields list must not be empty")
    return {k: v for k, v in record.items() if k in fields}


def add_field(record: dict, key: str, value: Any, overwrite: bool = False) -> dict:
    """Return a copy of record with a new field added.

    Raises TransformError if key already exists and overwrite is False.
    """
    if not key or not isinstance(key, str):
        raise TransformError("key must be a non-empty string")
    if key in record and not overwrite:
        raise TransformError(
            f"Field '{key}' already exists; use overwrite=True to replace it"
        )
    result = dict(record)
    result[key] = value
    return result


def apply_transforms(record: dict, transforms: list[dict]) -> dict:
    """Apply a sequence of transform descriptors to a record.

    Each descriptor is a dict with a 'op' key and operation-specific params:
      - {"op": "rename", "from": "old", "to": "new"}
      - {"op": "drop",   "fields": ["a", "b"]}
      - {"op": "keep",   "fields": ["a", "b"]}
      - {"op": "add",    "key": "k", "value": v, "overwrite": False}

    Raises TransformError on unknown op or missing params.
    """
    result = dict(record)
    for t in transforms:
        op = t.get("op")
        if op == "rename":
            result = rename_field(result, t["from"], t["to"])
        elif op == "drop":
            result = drop_fields(result, t.get("fields", []))
        elif op == "keep":
            result = keep_fields(result, t.get("fields", []))
        elif op == "add":
            result = add_field(
                result, t["key"], t["value"], overwrite=t.get("overwrite", False)
            )
        else:
            raise TransformError(f"Unknown transform op: '{op}'")
    return result
