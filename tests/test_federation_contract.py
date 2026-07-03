#!/usr/bin/env python3
"""Smoke test for the local Mac tools federation contract.

This test is fixture-only. It validates bundled federation files and never
runs a live disk audit, cleanup command, package install, app uninstall, or
live ledger write.
"""

from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
FEDERATION_DOC = ROOT / "FEDERATION.md"
CONTRACT_DIR = ROOT / "MAC_App_Audit"
SCHEMA = CONTRACT_DIR / "ledger-entry.schema.json"
LEDGER = CONTRACT_DIR / "example_ledger.json"
VALIDATOR = CONTRACT_DIR / "validate_ledger.py"


def fail(message):
    print(message, file=sys.stderr)
    return 1


def main():
    for path in [FEDERATION_DOC, SCHEMA, LEDGER, VALIDATOR]:
        if not path.exists():
            return fail(f"Missing required federation file: {path}")

    try:
        json.loads(SCHEMA.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return fail(f"Schema is not valid JSON: {exc}")

    result = subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            str(LEDGER),
            "--schema",
            str(SCHEMA),
        ],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return result.returncode

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    entries_by_id = {entry["entry_id"]: entry for entry in ledger}
    producers = {entry["producer"] for entry in ledger}

    required_producers = {"mac-app-audit", "freeup-space"}
    missing_producers = required_producers - producers
    if missing_producers:
        return fail(f"Example ledger missing producers: {sorted(missing_producers)}")

    has_cross_producer_seam = False
    for entry in ledger:
        producer = entry["producer"]
        for related_id in entry.get("related_entries", []):
            related = entries_by_id.get(related_id)
            if related and related.get("producer") != producer:
                has_cross_producer_seam = True
                break
        if has_cross_producer_seam:
            break

    if not has_cross_producer_seam:
        return fail("Example ledger lacks a cross-producer related_entries seam")

    doc = FEDERATION_DOC.read_text(encoding="utf-8")
    required_doc_phrases = [
        "/Users/o2satz/FreeUp-Space-Claude",
        "/Users/o2satz/FreeUp-Space-Claude/MAC_App_Audit",
        "freeup-space",
        "mac-app-audit",
        "related_entries",
    ]
    missing_doc_phrases = [phrase for phrase in required_doc_phrases if phrase not in doc]
    if missing_doc_phrases:
        return fail(f"FEDERATION.md missing phrases: {missing_doc_phrases}")

    print("Federation contract smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
