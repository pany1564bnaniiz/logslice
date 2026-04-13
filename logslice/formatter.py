"""Output formatters for logslice results."""

import json
from typing import Any, Dict, List, Optional


class FormatError(Exception):
    """Raised when output formatting fails."""


SUPPORTED_FORMATS = ("json", "logfmt", "pretty")


def format_json(record: Dict[str, Any], indent: Optional[int] = None) -> str:
    """Serialize a log record back to a JSON string."""
    try:
        return json.dumps(record, indent=indent, default=str)
    except (TypeError, ValueError) as exc:
        raise FormatError(f"Failed to serialize record to JSON: {exc}") from exc


def format_logfmt(record: Dict[str, Any]) -> str:
    """Serialize a log record to logfmt key=value pairs."""
    parts: List[str] = []
    for key, value in record.items():
        if value is None:
            parts.append(f"{key}=")
        elif isinstance(value, bool):
            parts.append(f"{key}={str(value).lower()}")
        elif isinstance(value, (dict, list)):
            serialized = json.dumps(value, default=str)
            escaped = serialized.replace('"', '\\"')
            parts.append(f'{key}="{escaped}"')
        elif isinstance(value, str) and (" " in value or "=" in value or '"' in value):
            escaped = value.replace('"', '\\"')
            parts.append(f'{key}="{escaped}"')
        else:
            parts.append(f"{key}={value}")
    return " ".join(parts)


def format_pretty(record: Dict[str, Any]) -> str:
    """Format a log record as a human-readable single line."""
    timestamp = record.get("time") or record.get("timestamp") or record.get("ts", "")
    level = record.get("level") or record.get("lvl") or record.get("severity", "")
    message = record.get("message") or record.get("msg", "")

    extras = {
        k: v
        for k, v in record.items()
        if k not in {"time", "timestamp", "ts", "level", "lvl", "severity", "message", "msg"}
    }

    parts = []
    if timestamp:
        parts.append(str(timestamp))
    if level:
        parts.append(f"[{str(level).upper()}]")
    if message:
        parts.append(str(message))
    if extras:
        extra_str = " ".join(f"{k}={v}" for k, v in extras.items())
        parts.append(extra_str)

    return " ".join(parts)


def format_record(record: Dict[str, Any], fmt: str = "json") -> str:
    """Dispatch formatting to the appropriate formatter."""
    if fmt not in SUPPORTED_FORMATS:
        raise FormatError(
            f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}"
        )
    if fmt == "json":
        return format_json(record)
    if fmt == "logfmt":
        return format_logfmt(record)
    return format_pretty(record)
