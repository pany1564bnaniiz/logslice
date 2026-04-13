"""Parser module for structured log files (JSON and logfmt)."""

import json
from typing import Optional


class LogParseError(Exception):
    """Raised when a log line cannot be parsed."""
    pass


def parse_json_line(line: str) -> dict:
    """Parse a single JSON-formatted log line.

    Args:
        line: A string containing a JSON log entry.

    Returns:
        A dictionary representing the log entry.

    Raises:
        LogParseError: If the line is not valid JSON or not a dict.
    """
    line = line.strip()
    if not line:
        raise LogParseError("Empty line")
    try:
        entry = json.loads(line)
    except json.JSONDecodeError as exc:
        raise LogParseError(f"Invalid JSON: {exc}") from exc
    if not isinstance(entry, dict):
        raise LogParseError("JSON log entry must be a JSON object")
    return entry


def parse_logfmt_line(line: str) -> dict:
    """Parse a single logfmt-formatted log line.

    Supports key=value and key="quoted value" pairs.

    Args:
        line: A string containing a logfmt log entry.

    Returns:
        A dictionary representing the log entry.

    Raises:
        LogParseError: If the line is empty or malformed.
    """
    line = line.strip()
    if not line:
        raise LogParseError("Empty line")

    entry: dict = {}
    i = 0
    length = len(line)

    while i < length:
        # Skip leading spaces
        while i < length and line[i] == " ":
            i += 1
        if i >= length:
            break

        # Read key
        key_start = i
        while i < length and line[i] not in ("=", " "):
            i += 1
        key = line[key_start:i]

        if i >= length or line[i] != "=":
            # Bare key with no value
            entry[key] = ""
            continue

        i += 1  # skip '='

        # Read value
        if i < length and line[i] == '"':
            i += 1  # skip opening quote
            val_chars = []
            while i < length:
                if line[i] == '\\' and i + 1 < length:
                    val_chars.append(line[i + 1])
                    i += 2
                elif line[i] == '"':
                    i += 1
                    break
                else:
                    val_chars.append(line[i])
                    i += 1
            entry[key] = "".join(val_chars)
        else:
            val_start = i
            while i < length and line[i] != " ":
                i += 1
            entry[key] = line[val_start:i]

    return entry


def detect_format(line: str) -> Optional[str]:
    """Attempt to detect the format of a log line.

    Returns:
        'json', 'logfmt', or None if unknown.
    """
    stripped = line.strip()
    if stripped.startswith("{"):
        return "json"
    if "=" in stripped:
        return "logfmt"
    return None
