#!/usr/bin/env python3
"""
validate_ledger.py — validates a ledger JSON file against the federation
schema.

Usage:
    python3 validate_ledger.py <path-to-ledger.json>
    python3 validate_ledger.py <path-to-ledger.json> --schema <path-to-schema.json>

Exit codes:
    0 — every entry valid
    1 — one or more entries invalid, or the file itself isn't a JSON array
    2 — usage/environment error (missing file, missing dependency, bad JSON)

No network access, no writes. Reads the ledger file and the schema file
only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print(
        "ERROR: this validator requires the 'jsonschema' package.\n"
        "Install with: pip3 install jsonschema  (or: pip3 install jsonschema --break-system-packages)",
        file=sys.stderr,
    )
    sys.exit(2)


def default_schema_path() -> Path:
    """Find the schema in either the flat bundle or canonical layout."""
    script_dir = Path(__file__).resolve().parent
    flat_schema = script_dir / "ledger-entry.schema.json"
    if flat_schema.exists():
        return flat_schema
    return script_dir.parent / "schema" / "ledger-entry.schema.json"


def load_json(path: Path, label: str) -> object:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {label} not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"ERROR: {label} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(2)


def validate_ledger(ledger_path: Path, schema_path: Path) -> int:
    schema = load_json(schema_path, "schema file")
    ledger = load_json(ledger_path, "ledger file")

    if not isinstance(ledger, list):
        print(
            f"ERROR: ledger file must be a JSON array of entries, got {type(ledger).__name__}",
            file=sys.stderr,
        )
        return 1

    validator = jsonschema.Draft7Validator(schema)
    error_count = 0

    for i, entry in enumerate(ledger):
        errors = sorted(validator.iter_errors(entry), key=lambda e: e.path)
        if errors:
            error_count += 1
            subject_name = ""
            if isinstance(entry, dict):
                subject_name = entry.get("subject", {}).get("name", "") if isinstance(entry.get("subject"), dict) else ""
                entry_id = entry.get("entry_id", "<no entry_id>")
            else:
                entry_id = "<not an object>"
            print(f"INVALID entry[{i}] (entry_id={entry_id!r}, subject={subject_name!r}):", file=sys.stderr)
            for err in errors:
                loc = "/".join(str(p) for p in err.path) or "<root>"
                print(f"  - at {loc}: {err.message}", file=sys.stderr)

    total = len(ledger)
    valid = total - error_count

    if error_count == 0:
        print(f"OK: {valid}/{total} entries valid.")
        return 0
    else:
        print(f"FAILED: {valid}/{total} entries valid, {error_count} invalid.", file=sys.stderr)
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a federation ledger file against the ledger-entry schema.")
    parser.add_argument("ledger_path", type=Path, help="Path to the ledger JSON file to validate.")
    parser.add_argument(
        "--schema",
        type=Path,
        default=default_schema_path(),
        help=f"Path to the schema file (default: {default_schema_path()})",
    )
    args = parser.parse_args()

    exit_code = validate_ledger(args.ledger_path, args.schema)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
