"""Field redaction and masking utilities for log records."""

import re
from typing import Any, Dict, Iterable, List, Optional


class RedactorError(Exception):
    """Raised when a redaction operation fails."""


def redact_field(
    record: Dict[str, Any],
    field: str,
    mask: str = "***",
) -> Dict[str, Any]:
    """Return a copy of *record* with *field* replaced by *mask*.

    Raises RedactorError if *field* does not exist in the record.
    """
    if not field:
        raise RedactorError("field name must not be empty")
    if field not in record:
        raise RedactorError(f"field '{field}' not found in record")
    result = dict(record)
    result[field] = mask
    return result


def redact_pattern(
    record: Dict[str, Any],
    pattern: str,
    mask: str = "***",
    fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Return a copy of *record* with regex *pattern* replaced by *mask*.

    If *fields* is given, only those fields are scanned; otherwise all
    string-valued fields are scanned.

    Raises RedactorError if *pattern* is not a valid regular expression.
    """
    if not pattern:
        raise RedactorError("pattern must not be empty")
    try:
        compiled = re.compile(pattern)
    except re.error as exc:
        raise RedactorError(f"invalid pattern '{pattern}': {exc}") from exc

    result = dict(record)
    target_fields = fields if fields is not None else list(result.keys())
    for key in target_fields:
        value = result.get(key)
        if isinstance(value, str):
            result[key] = compiled.sub(mask, value)
    return result


def apply_redactions(
    records: Iterable[Dict[str, Any]],
    redact_fields: Optional[List[str]] = None,
    redact_pattern_str: Optional[str] = None,
    mask: str = "***",
    pattern_fields: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """Apply field and/or pattern redactions to a sequence of records.

    Returns a new list of redacted records without mutating the originals.
    """
    output: List[Dict[str, Any]] = []
    for record in records:
        r = dict(record)
        if redact_fields:
            for field in redact_fields:
                if field in r:
                    r[field] = mask
        if redact_pattern_str:
            r = redact_pattern(r, redact_pattern_str, mask=mask, fields=pattern_fields)
        output.append(r)
    return output
