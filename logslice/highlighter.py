"""Terminal syntax highlighting for log records."""

import re
from typing import Any

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_RED = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_CYAN = "\033[36m"
ANSI_MAGENTA = "\033[35m"
ANSI_DIM = "\033[2m"

LEVEL_COLORS = {
    "error": ANSI_RED,
    "err": ANSI_RED,
    "fatal": ANSI_RED,
    "critical": ANSI_RED,
    "warn": ANSI_YELLOW,
    "warning": ANSI_YELLOW,
    "info": ANSI_GREEN,
    "debug": ANSI_DIM,
    "trace": ANSI_DIM,
}


class HighlightError(Exception):
    """Raised when highlighting fails."""


def _colorize(text: str, color: str) -> str:
    return f"{color}{text}{ANSI_RESET}"


def highlight_level(record: dict[str, Any], level_field: str = "level") -> str:
    """Return a colorized string for the log level value."""
    level = record.get(level_field, "")
    if not isinstance(level, str):
        level = str(level)
    color = LEVEL_COLORS.get(level.lower(), "")
    if color:
        return _colorize(level, color + ANSI_BOLD)
    return level


def highlight_field_value(value: Any, pattern: str) -> str:
    """Wrap regex pattern matches within a string value with highlight color."""
    if not isinstance(value, str):
        value = str(value)
    if not pattern:
        raise HighlightError("Pattern must not be empty.")
    try:
        highlighted = re.sub(
            pattern,
            lambda m: _colorize(m.group(0), ANSI_MAGENTA + ANSI_BOLD),
            value,
        )
    except re.error as exc:
        raise HighlightError(f"Invalid pattern '{pattern}': {exc}") from exc
    return highlighted


def highlight_record(
    record: dict[str, Any],
    level_field: str = "level",
    highlight_pattern: str | None = None,
) -> dict[str, Any]:
    """Return a copy of the record with display-ready highlighted values.

    - The level field is colorized by severity.
    - If highlight_pattern is given, all string values matching the pattern
      are wrapped with a highlight color.
    """
    if not isinstance(record, dict):
        raise HighlightError("Record must be a dict.")

    result: dict[str, Any] = {}
    for key, value in record.items():
        if key == level_field:
            result[key] = highlight_level(record, level_field)
        elif highlight_pattern and isinstance(value, str):
            result[key] = highlight_field_value(value, highlight_pattern)
        else:
            result[key] = value
    return result
