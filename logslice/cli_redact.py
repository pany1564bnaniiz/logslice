"""CLI helpers for the --redact-field and --redact-pattern options."""

import argparse
from typing import Any, Dict, Iterable, List

from logslice.redactor import apply_redactions


def add_redact_args(parser: argparse.ArgumentParser) -> None:
    """Register redaction-related arguments on *parser*."""
    parser.add_argument(
        "--redact-field",
        metavar="FIELD",
        action="append",
        dest="redact_fields",
        default=[],
        help="Redact the value of FIELD in every record (repeatable).",
    )
    parser.add_argument(
        "--redact-pattern",
        metavar="REGEX",
        dest="redact_pattern",
        default=None,
        help="Replace matches of REGEX with the mask string in all string fields.",
    )
    parser.add_argument(
        "--redact-mask",
        metavar="MASK",
        dest="redact_mask",
        default="***",
        help="Mask string used as the replacement value (default: ***).",
    )
    parser.add_argument(
        "--redact-pattern-fields",
        metavar="FIELD",
        action="append",
        dest="redact_pattern_fields",
        default=None,
        help=(
            "Limit --redact-pattern to these fields only (repeatable). "
            "If omitted, all string fields are scanned."
        ),
    )


def run_redact(
    records: Iterable[Dict[str, Any]],
    args: argparse.Namespace,
) -> List[Dict[str, Any]]:
    """Apply redactions described by *args* to *records* and return the result.

    Reads the following attributes from *args*:
      - redact_fields: list[str]
      - redact_pattern: str | None
      - redact_mask: str
      - redact_pattern_fields: list[str] | None
    """
    redact_fields: List[str] = getattr(args, "redact_fields", []) or []
    redact_pattern: str | None = getattr(args, "redact_pattern: str = getattr(args, "redact_mask", "***")
    pattern_fields: List[str] | None = getattr(args, "redact_pattern_fields", None)

    if not redact_fields and not redact_pattern:
        return(records)

    return apply_redactions(
        records,
        redact_fields=redact_fields if redact_fields else None,
        redact_pattern_str=redact_pattern,
        mask=mask,
        pattern_fields=pattern_fields,
    )
