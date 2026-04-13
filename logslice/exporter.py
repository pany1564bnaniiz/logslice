"""Export filtered log records to various output formats and destinations."""

import json
import csv
import io
from typing import List, Dict, Any, Optional


class ExportError(Exception):
    """Raised when an export operation fails."""


def export_jsonl(records: List[Dict[str, Any]]) -> str:
    """Export records as newline-delimited JSON (JSONL)."""
    if not isinstance(records, list):
        raise ExportError("records must be a list")
    lines = []
    for record in records:
        try:
            lines.append(json.dumps(record, default=str))
        except (TypeError, ValueError) as e:
            raise ExportError(f"Failed to serialize record to JSON: {e}") from e
    return "\n".join(lines)


def export_csv(
    records: List[Dict[str, Any]],
    fieldnames: Optional[List[str]] = None,
    delimiter: str = ",",
) -> str:
    """Export records as CSV.

    If fieldnames is not provided, the union of all keys from all records is used,
    sorted alphabetically.
    """
    if not isinstance(records, list):
        raise ExportError("records must be a list")
    if not records:
        return ""
    if fieldnames is None:
        keys: set = set()
        for r in records:
            keys.update(r.keys())
        fieldnames = sorted(keys)
    if not fieldnames:
        raise ExportError("fieldnames must not be empty")
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        delimiter=delimiter,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for record in records:
        writer.writerow({k: record.get(k, "") for k in fieldnames})
    return output.getvalue()


def export_tsv(
    records: List[Dict[str, Any]],
    fieldnames: Optional[List[str]] = None,
) -> str:
    """Export records as tab-separated values (TSV)."""
    return export_csv(records, fieldnames=fieldnames, delimiter="\t")


def export_records(
    records: List[Dict[str, Any]],
    fmt: str,
    fieldnames: Optional[List[str]] = None,
) -> str:
    """Dispatch export to the appropriate format handler.

    Supported formats: 'jsonl', 'csv', 'tsv'.
    """
    fmt = fmt.lower()
    if fmt == "jsonl":
        return export_jsonl(records)
    elif fmt == "csv":
        return export_csv(records, fieldnames=fieldnames)
    elif fmt == "tsv":
        return export_tsv(records, fieldnames=fieldnames)
    else:
        raise ExportError(f"Unsupported export format: '{fmt}'. Choose from: jsonl, csv, tsv")
