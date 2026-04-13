"""Field validation for log records."""

from typing import Any, Dict, List, Optional


class ValidatorError(Exception):
    """Raised when validation configuration or execution fails."""


def require_fields(record: Dict[str, Any], fields: List[str]) -> bool:
    """Return True if all required fields are present and non-empty in the record.

    Args:
        record: A parsed log record.
        fields: Field names that must be present.

    Raises:
        ValidatorError: If fields list is empty or contains blank names.
    """
    if not fields:
        raise ValidatorError("fields list must not be empty")
    for f in fields:
        if not f or not f.strip():
            raise ValidatorError("field name must not be blank")
    return all(f in record and record[f] not in (None, "") for f in fields)


def require_field_type(
    record: Dict[str, Any], field: str, expected_type: type
) -> bool:
    """Return True if the field exists and its value matches expected_type.

    Args:
        record: A parsed log record.
        field: The field name to check.
        expected_type: The Python type the field value should be.

    Raises:
        ValidatorError: If field is blank or expected_type is not a type.
    """
    if not field or not field.strip():
        raise ValidatorError("field name must not be blank")
    if not isinstance(expected_type, type):
        raise ValidatorError("expected_type must be a Python type")
    if field not in record:
        return False
    return isinstance(record[field], expected_type)


def apply_validations(
    records: List[Dict[str, Any]],
    required_fields: Optional[List[str]] = None,
    field_type: Optional[tuple] = None,
) -> List[Dict[str, Any]]:
    """Filter records that pass all configured validations.

    Args:
        records: List of parsed log records.
        required_fields: If given, records must contain all listed fields.
        field_type: If given, a (field_name, type) tuple; records must have
                    the field with the correct type.

    Returns:
        A list of records that satisfy every active validation.

    Raises:
        ValidatorError: If validation configuration is invalid.
    """
    result = []
    for record in records:
        if required_fields is not None:
            if not require_fields(record, required_fields):
                continue
        if field_type is not None:
            fname, ftype = field_type
            if not require_field_type(record, fname, ftype):
                continue
        result.append(record)
    return result
