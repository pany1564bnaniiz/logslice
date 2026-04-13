# logslice

A CLI tool for filtering and slicing structured log files by time range, level, or field patterns.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/youruser/logslice.git
cd logslice && pip install -e .
```

---

## Usage

```bash
# Filter logs by time range
logslice --file app.log --start "2024-01-15T08:00:00" --end "2024-01-15T09:00:00"

# Filter by log level
logslice --file app.log --level ERROR

# Filter by field pattern
logslice --file app.log --match "user_id=42"

# Combine filters
logslice --file app.log --level WARN --start "2024-01-15T08:00:00" --match "service=auth"

# Output to a file
logslice --file app.log --level ERROR --out errors.log
```

### Supported Formats

- JSON (newline-delimited)
- Logfmt
- Common log formats (Apache, Nginx)

---

## Options

| Flag | Description |
|------|-------------|
| `--file` | Path to the log file |
| `--start` | Start of time range (ISO 8601) |
| `--end` | End of time range (ISO 8601) |
| `--level` | Filter by log level (DEBUG, INFO, WARN, ERROR) |
| `--match` | Filter by field pattern (`key=value`) |
| `--out` | Write output to a file instead of stdout |

---

## License

MIT © 2024 youruser