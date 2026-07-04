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
    2 — usage/environment error (missing file, bad JSON)

No network access, no writes. Reads the ledger file and the schema file
only.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    jsonschema = None


class FallbackValidationError:
    """Small error shape matching the fields this CLI prints from jsonschema."""

    def __init__(self, path: tuple[object, ...], message: str) -> None:
        self.path = path
        self.message = message


def value_type_name(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return type(value).__name__


def type_matches(expected_type: object, value: object) -> bool:
    if isinstance(expected_type, list):
        return any(type_matches(item, value) for item in expected_type)
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return True


def expected_type_label(expected_type: object) -> str:
    if isinstance(expected_type, list):
        return " or ".join(str(item) for item in expected_type)
    return str(expected_type)


def iter_fallback_errors(
    value: object,
    schema: object,
    path: tuple[object, ...] = (),
):
    """Validate the Draft 7 subset used by ledger-entry.schema.json."""
    if not isinstance(schema, dict):
        return

    expected_type = schema.get("type")
    if expected_type is not None and not type_matches(expected_type, value):
        yield FallbackValidationError(
            path,
            f"{value_type_name(value)!r} is not of type {expected_type_label(expected_type)!r}",
        )
        return

    if "enum" in schema and value not in schema["enum"]:
        allowed = ", ".join(repr(item) for item in schema["enum"])
        yield FallbackValidationError(path, f"{value!r} is not one of [{allowed}]")

    if isinstance(value, str):
        min_length = schema.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            yield FallbackValidationError(path, f"{value!r} is too short")

        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            yield FallbackValidationError(path, f"{value!r} does not match {pattern!r}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            yield FallbackValidationError(path, f"{value!r} is less than the minimum of {minimum!r}")

        maximum = schema.get("maximum")
        if isinstance(maximum, (int, float)) and value > maximum:
            yield FallbackValidationError(path, f"{value!r} is greater than the maximum of {maximum!r}")

    if isinstance(value, dict):
        required = schema.get("required", [])
        if isinstance(required, list):
            for key in required:
                if isinstance(key, str) and key not in value:
                    yield FallbackValidationError(path, f"{key!r} is a required property")

        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, subschema in properties.items():
                if key in value:
                    yield from iter_fallback_errors(value[key], subschema, path + (key,))

        if schema.get("additionalProperties") is False and isinstance(properties, dict):
            for key in value:
                if key not in properties:
                    yield FallbackValidationError(path + (key,), "additional properties are not allowed")

    if isinstance(value, list):
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                yield from iter_fallback_errors(item, item_schema, path + (index,))


def iter_validation_errors(entry: object, schema: object):
    if jsonschema is not None:
        validator = jsonschema.Draft7Validator(schema)
        yield from validator.iter_errors(entry)
    else:
        yield from iter_fallback_errors(entry, schema)


def error_sort_key(error: object) -> tuple[str, ...]:
    return tuple(str(part) for part in getattr(error, "path", ()))


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

    error_count = 0

    for i, entry in enumerate(ledger):
        errors = sorted(iter_validation_errors(entry, schema), key=error_sort_key)
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
