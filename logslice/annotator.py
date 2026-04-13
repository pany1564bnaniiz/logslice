"""Field annotation utilities for logslice.

Allows adding computed or static annotations to log records,
such as tagging records with a source label or derived fields.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


class AnnotatorError(Exception):
    """Raised when an annotation operation fails."""


def annotate_static(
    record: Dict[str, Any],
    field: str,
    value: Any,
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Return a copy of *record* with *field* set to *value*.

    Args:
        record: The source record.
        field: The field name to add or update.
        value: The static value to assign.
        overwrite: If False (default), raises AnnotatorError whenfield*
                   already exists in the record.

    Returns:
        A new dict with the annotation applied.

    Raises:
        AnnotatorError: If *field* is empty or already exists and
                        *overwrite* is False.
    """
    if not field or not field.strip():
        raise AnnotatorError("field name must not be empty")
    if field in record and not overwrite:
        raise AnnotatorError(
            f"field '{field}' already exists; pass overwrite=True to replace it"
        )
    return {**record, field: value}


def annotate_derived(
    record: Dict[str, Any],
    field: str,
    fn: Callable[[Dict[str, Any]], Any],
    overwrite: bool = False,
) -> Dict[str, Any]:
    """Return a copy of *record* with *field* set to the result of *fn(record)*.

    Args:
        record: The source log record.
        field: The field name to add or update.
        fn: A callable that receives the record and returns the new value.
        overwrite: If False (default), raises AnnotatorError when *field*
                   already exists.

    Returns:
        A new dict with the derived annotation applied.

    Raises:
        AnnotatorError: If *field* is empty, already exists without overwrite,
                        or *fn* raises an exception.
    """
    if not field or not field.strip():
        raise AnnotatorError("field name must not be empty")
    if field in record and not overwrite:
        raise AnnotatorError(
            f"field '{field}' already exists; pass overwrite=True to replace it"
        )
    try:
        computed = fn(record)
    except Exception as exc:  # noqa: BLE001
        raise AnnotatorError(f"annotation function raised an error: {exc}") from exc
    return {**record, field: computed}


def apply_annotations(
    records: List[Dict[str, Any]],
    annotations: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Apply a list of annotation specs to every record.

    Each spec dict must contain:
        - ``field`` (str): target field name.
        - ``value`` (Any, optional): static value.
        - ``fn`` (callable, optional): derived-value callable.
        - ``overwrite`` (bool, optional): defaults to False.

    Exactly one of ``value`` or ``fn`` must be provided per spec.

    Raises:
        AnnotatorError: If a spec is malformed or annotation fails.
    """
    result = []
    for record in records:
        current = record
        for spec in annotations:
            field = spec.get("field", "")
            overwrite = bool(spec.get("overwrite", False))
            if "fn" in spec and "value" in spec:
                raise AnnotatorError(
                    "annotation spec must not specify both 'value' and 'fn'"
                )
            if "fn" in spec:
                current = annotate_derived(current, field, spec["fn"], overwrite)
            elif "value" in spec:
                current = annotate_static(current, field, spec["value"], overwrite)
            else:
                raise AnnotatorError(
                    "annotation spec must specify either 'value' or 'fn'"
                )
        result.append(current)
    return result
