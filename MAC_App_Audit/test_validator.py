#!/usr/bin/env python3
"""Smoke tests for the flat MAC_App_Audit federation validator bundle.

Run directly from this directory:
    python3 test_validator.py

The test validates local fixture files only. It does not write live ledgers,
install packages, run audits, or execute cleanup actions.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

CONTRACT_ROOT = Path(__file__).resolve().parent
VALIDATOR = CONTRACT_ROOT / "validate_ledger.py"
SCHEMA = CONTRACT_ROOT / "ledger-entry.schema.json"
GOOD_LEDGER = CONTRACT_ROOT / "example_ledger.json"


def run_validator(ledger_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(ledger_path), "--schema", str(SCHEMA)],
        capture_output=True,
        text=True,
    )


def run_validator_with_default_schema(ledger_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(ledger_path)],
        capture_output=True,
        text=True,
    )


def check(condition: bool, description: str, failures: list[str]) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {description}")
    if not condition:
        failures.append(description)


def main() -> None:
    failures: list[str] = []

    assert VALIDATOR.exists(), f"validator script missing at {VALIDATOR}"
    assert SCHEMA.exists(), f"schema missing at {SCHEMA}"
    assert GOOD_LEDGER.exists(), f"example ledger missing at {GOOD_LEDGER}"

    good_result = run_validator(GOOD_LEDGER)
    check(
        good_result.returncode == 0,
        f"validator exits 0 on the good example ledger (got {good_result.returncode})",
        failures,
    )
    check(
        "OK:" in good_result.stdout,
        "validator prints an OK summary line for the good ledger",
        failures,
    )

    default_schema_result = run_validator_with_default_schema(GOOD_LEDGER)
    check(
        default_schema_result.returncode == 0,
        f"validator finds the flat-bundle schema by default (got {default_schema_result.returncode})",
        failures,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        bad_ledger = Path(tmpdir) / "fixtures_invalid_ledger.json"
        bad_ledger.write_text('[{"entry_id": "missing-required-fields"}]', encoding="utf-8")
        bad_result = run_validator(bad_ledger)
        check(
            bad_result.returncode == 1,
            f"validator exits 1 on the intentionally invalid ledger (got {bad_result.returncode})",
            failures,
        )
        check(
            "INVALID entry" in bad_result.stderr,
            "validator reports per-entry INVALID errors on stderr for the broken ledger",
            failures,
        )
        check(
            "FAILED:" in bad_result.stderr,
            "validator prints a FAILED summary line for the broken ledger",
            failures,
        )

    missing_result = run_validator(CONTRACT_ROOT / "does" / "not" / "exist.json")
    check(
        missing_result.returncode == 2,
        f"validator exits 2 on a missing file (got {missing_result.returncode})",
        failures,
    )

    print()
    if failures:
        print(f"{len(failures)} check(s) failed:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("All checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
