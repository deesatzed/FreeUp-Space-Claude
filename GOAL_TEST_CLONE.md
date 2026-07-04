# GOAL_TEST_CLONE.md - Fresh Clone Federation Test Contract

Use this file after cloning the repository and starting a new Codex session.

Suggested setup before running the goal:

```bash
git clone https://github.com/deesatzed/FreeUp-Space-Claude.git
cd FreeUp-Space-Claude
```

Then run:

```text
/goal GOAL_TEST_CLONE.md
```

## OUTCOME

Complete a fresh-clone verification session proving that the GitHub checkout of
FreeUp Space contains a working safety-first CLI, a valid local Mac Tools
Federation contract, and a working `MAC_App_Audit` flat contract bundle.

The test session must prove all three surfaces from a newly cloned checkout:

1. FreeUp Space v0.2 CLI/report functionality.
2. Mac Tools Federation file contract and cross-producer ledger seam.
3. `MAC_App_Audit` validator/schema/example-ledger bundle.

This goal is a verification goal, not an implementation goal. Do not add
features unless a small test harness repair is required to make a documented
verification command accurately test the intended behavior.

## PROOF OF DONE

Run from the freshly cloned repository root.

### 1. Fresh Clone Identity

```bash
pwd
git status --short --branch
git remote -v
git rev-parse HEAD
git log --oneline -3
```

Confirm:

- The working tree starts clean.
- `origin` points to `https://github.com/deesatzed/FreeUp-Space-Claude.git`.
- The checkout contains `AGENTS.md`, `GOAL.md`, `GOAL_TEST_CLONE.md`,
  `FEDERATION.md`, `README.md`, `install.sh`, `uninstall.sh`,
  `scripts/freeup_space.py`, and `MAC_App_Audit/`.

### 2. Documentation And Boundary Inspection

Read:

```bash
sed -n '1,220p' AGENTS.md
sed -n '1,260p' FEDERATION.md
sed -n '1,220p' README.md
sed -n '1,220p' MAC_App_Audit/README.md
sed -n '1,220p' MAC_App_Audit/CONVENTIONS.md
sed -n '1,220p' MAC_App_Audit/SAFETY_CONTRACT.md
```

Confirm by inspection:

- FreeUp Space owns disk-space and reclaimable-storage findings.
- mac-app-audit owns app/tool-choice and Homebrew package findings.
- Cross-product seams use ledger `related_entries`.
- There is no umbrella CLI, daemon, telemetry service, cleanup execution, or
  app uninstall execution in v0.1.

### 3. FreeUp Space Static And Fixture Validation

```bash
git diff --check
bash -n scripts/disk_audit.sh
bash -n install.sh
bash -n uninstall.sh
python3 -m py_compile scripts/generate_report.py
python3 -m py_compile scripts/freeup_space.py
python3 tests/smoke_test.py
python3 tests/test_cli_smoke.py
python3 scripts/freeup_space.py --help
python3 scripts/freeup_space.py doctor
python3 scripts/freeup_space.py report --input tests/fixtures/sample_audit.txt --output /tmp/freeup-space-clone-report.md
test -s /tmp/freeup-space-clone-report.md
```

Confirm:

- Help lists `audit`, `report`, `doctor`, `dev`, `models`, and `plan`.
- Doctor reports Python, Bash, Desktop, repo script paths, and macOS optional
  tools or non-macOS graceful status.
- The generated report contains `# Mac Disk Cleanup Report` and `## Top Findings`.
- No cleanup command executes.

### 4. Sandboxed Install/Uninstall Verification

Use a temporary HOME so the test never alters the user's real
`~/.local/bin/freeup-space` wrapper:

```bash
TMP_HOME="$(mktemp -d)"
mkdir -p "$TMP_HOME/Desktop"
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" bash install.sh
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" freeup-space --help
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" freeup-space doctor
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" freeup-space report --input tests/fixtures/sample_audit.txt --output /tmp/freeup-space-clone-wrapper-report.md
test -s /tmp/freeup-space-clone-wrapper-report.md
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" bash uninstall.sh
test ! -e "$TMP_HOME/.local/bin/freeup-space"
rm -rf "$TMP_HOME"
```

Confirm:

- The wrapper is installed only under the temporary HOME.
- The wrapper can run help, doctor, and report commands.
- The uninstaller removes only the temporary wrapper.
- No real user reports, audit files, repository files, or user data are removed.

### 5. MAC_App_Audit Contract Bundle Validation

```bash
cd MAC_App_Audit
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 validate_ledger.py example_ledger.json
python3 test_validator.py
cd ..
```

Confirm:

- The explicit schema validation prints `OK: 5/5 entries valid.`
- The default-schema validation also works in the flat bundle layout.
- `test_validator.py` accepts the good ledger, rejects an intentionally invalid
  ledger, and reports a missing file as an environment error.
- Validation works even when `jsonschema` is not installed, using the bundled
  standard-library fallback. Do not install packages during this proof.

### 6. Federation Smoke And Ledger Seam Validation

```bash
python3 tests/test_federation_contract.py
python3 - <<'PY'
import json
from pathlib import Path

ledger = json.loads(Path("MAC_App_Audit/example_ledger.json").read_text())
entries = {entry["entry_id"]: entry for entry in ledger}
producers = sorted({entry["producer"] for entry in ledger})
seams = []
for entry in ledger:
    for related_id in entry.get("related_entries", []):
        related = entries.get(related_id)
        if related and related["producer"] != entry["producer"]:
            seams.append((entry["entry_id"], entry["producer"], related_id, related["producer"]))

print("producers:", ", ".join(producers))
print("cross_producer_seams:", len(seams))
for seam in seams:
    print(" -> ".join(seam))
PY
```

Confirm:

- `tests/test_federation_contract.py` exits 0.
- Producers include both `freeup-space` and `mac-app-audit`.
- At least one cross-producer seam exists.

### 7. Optional macOS-Only Live Read-Only Audit

Run this only on macOS and only if a live audit is acceptable for the session.
It is read-only but can take time on large home directories:

```bash
python3 scripts/freeup_space.py audit --output /tmp/freeup-space-clone-audit.txt
python3 scripts/freeup_space.py report --input /tmp/freeup-space-clone-audit.txt --output /tmp/freeup-space-clone-live-report.md
test -s /tmp/freeup-space-clone-live-report.md
```

Do not run any cleanup command suggested by the generated report.

### 8. Final Artifact And Safety Checks

```bash
find . \( -name __pycache__ -o -name '*.pyc' -o -name '*test.ledger.json' -o -name '*freeup-space-clone-*.md' -o -name '*freeup-space-clone-*.txt' \) -print
rg -n "sudo|rm -rf|trash|brew uninstall|pip install|launchd|daemon|telemetry|live ledger|cleanup command|app uninstall" FEDERATION.md AGENTS.md README.md scripts tests MAC_App_Audit
git status --short --branch
```

Confirm:

- Any repo-local `__pycache__` or `.pyc` artifacts are removed before completion.
- The `rg` hits are safety/documentation references or inert recommendation text,
  not default runtime execution paths.
- The fresh clone remains clean, unless the session intentionally created and
  removed temporary files outside the repo.

## SCOPE

Allowed:

- Read and inspect repository files.
- Run fixture-based tests and validators.
- Run FreeUp CLI help, doctor, and fixture report commands.
- Run installer/uninstaller only with a temporary HOME.
- Run optional live read-only audit on macOS only if acceptable.
- If a verification command fails because of a repo bug, make the smallest
  repair needed, then rerun the failed and adjacent checks.

Do not modify unless needed for a verification bug:

- `scripts/disk_audit.sh`
- `scripts/generate_report.py`
- `scripts/freeup_space.py`
- `install.sh`
- `uninstall.sh`
- `MAC_App_Audit/validate_ledger.py`
- `MAC_App_Audit/test_validator.py`
- docs or tests

Do not modify:

- user data outside the clone,
- live ledgers under `~/.local/share/mac-tools-federation/`,
- the user's real `~/.local/bin/freeup-space`,
- git remotes or branches,
- production/deployment settings.

## CONSTRAINTS

- Keep every audit and test path read-only with respect to user data.
- Do not execute cleanup, cache-clearing, snapshot-thinning, app uninstall,
  package install, migration, telemetry, daemon setup, or `sudo` commands.
- Do not add dependencies during the test session without explicit approval.
- Do not create an umbrella CLI or shared runtime.
- Do not weaken safety language or tests to make the session pass.
- Treat fixture validation as sufficient for CI-style clone verification.
- Treat optional live audit as additional evidence only, not required proof.

## SAFETY / PROVENANCE

- Federation entries are decision records, not actions.
- FreeUp Space recommendations are report text only unless a future separate
  approved execution goal exists.
- MAC_App_Audit recommendations are software-choice records only unless a future
  separate approved execution goal exists.
- Cross-product federation happens through file reads and `related_entries`, not
  hidden code calls.
- If evidence is missing, report uncertainty instead of claiming completion.

## ITERATION

1. Start by proving the clone identity and clean state.
2. Run documentation and boundary inspection before tests.
3. Run FreeUp fixture validation.
4. Run sandboxed install/uninstall validation with temporary HOME.
5. Run MAC_App_Audit validator validation.
6. Run federation smoke and ledger seam validation.
7. Optionally run a live macOS read-only audit.
8. Remove generated repo-local artifacts.
9. Summarize pass/fail results with exact commands and any remaining risk.

## STOP

Stop and summarize if:

- The clone is not from `https://github.com/deesatzed/FreeUp-Space-Claude.git`.
- Required files are missing from the cloned checkout.
- A command would touch real user install paths, user data, or live ledgers.
- Any requested path would execute cleanup, app uninstall, package install,
  `sudo`, telemetry, daemon setup, or live ledger mutation.
- The same failure persists after three distinct repair attempts.

## COMPLETE

Mark complete only when:

1. Fresh clone identity is verified.
2. FreeUp Space static, fixture, CLI, and sandboxed install tests pass.
3. MAC_App_Audit validator tests pass in the flat bundle layout.
4. Federation smoke test passes.
5. The example ledger proves both producers and a cross-producer seam.
6. No cleanup or app-uninstall execution occurred.
7. Repo-local generated artifacts are absent.
8. The final summary separates required proof, optional live-audit proof, and
   deferred future work.
