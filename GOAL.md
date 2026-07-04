# GOAL.md - FreeUp Space + MAC_App_Audit Federation Completion Contract

## Source Of Truth

This goal is grounded in the current checkout at
`/Users/o2satz/FreeUp-Space-Claude` and these files:

- `AGENTS.md`
- `README.md`
- `SKILL.md`
- `scripts/disk_audit.sh`
- `scripts/generate_report.py`
- `scripts/freeup_space.py`
- `install.sh`
- `uninstall.sh`
- `tests/smoke_test.py`
- `tests/test_cli_smoke.py`
- `MAC_App_Audit/HANDOFF_2026-07-03.md`
- `MAC_App_Audit/HANDOFF_LATEST.md`
- `MAC_App_Audit/HANDOFF_v0.1.md`
- `MAC_App_Audit/GOAL.md`
- `MAC_App_Audit/README.md`
- `MAC_App_Audit/SAFETY_CONTRACT.md`
- `MAC_App_Audit/CONVENTIONS.md`
- `MAC_App_Audit/ledger-entry.schema.json`
- `MAC_App_Audit/example_ledger.json`
- `MAC_App_Audit/validate_ledger.py`
- `MAC_App_Audit/test_validator.py`

The active objective is to complete a local file-based Mac tools federation
that includes both:

1. `freeup-space`: the safety-first disk-space and reclaimable-storage product.
2. `mac-app-audit`: the safety-first app/tool-choice and software-audit product.

The federation must let the two tools share a ledger schema, safety posture,
and cross-reference convention without merging codebases or adding an umbrella
runtime.

## Current Truth From The 2026-07-03 Handoff

`MAC_App_Audit/HANDOFF_2026-07-03.md` adds these current-state facts that must
drive the next autonomous run:

1. `MAC_App_Audit/` currently contains a flat local copy of
   `mac-tools-federation` contract files plus a `GOAL.md` for a planned
   `mac-app-audit v0.2` build.
2. The folder is not yet the complete `mac-app-audit` implementation root
   described by `MAC_App_Audit/HANDOFF_v0.1.md`.
3. The actual app implementation files named by `HANDOFF_v0.1.md` are absent
   from `MAC_App_Audit/`: `SKILL.md`, `scripts/collect_inventory.sh`,
   `commands/audit-apps.md`, and `tests/fixtures/mac_apps_report.txt`.
4. The flat-layout validator command works:

   ```bash
   cd MAC_App_Audit
   python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
   ```

   Expected output includes `OK: 5/5 entries valid.`

5. `MAC_App_Audit/test_validator.py` is currently broken because it expects the
   canonical standalone federation layout:
   `validator/validate_ledger.py`, `examples/example_ledger.json`, and
   `tests/fixtures_invalid_ledger.json` under the parent repo root.
6. The P0 blockers are repo identity/layout and validator smoke-test alignment.
7. Parent FreeUp Space is a separate storage-audit product and must not be
   mixed with app-audit implementation logic.
8. `MAC_App_Audit/` is untracked in the parent git repo at handoff time, and
   the parent repo also contains uncommitted FreeUp v0.2 work.

## Product North Star

Mac Tools Federation is not a new app. It is the file contract that lets
independent local Mac tools coordinate decisions safely:

- FreeUp Space owns disk-space findings: caches, rebuildable artifacts, large
  files, local model bytes, and reclaimable storage.
- mac-app-audit owns software-choice findings: apps, Homebrew formulae/casks,
  redundant tools, superseded tools, keep decisions, and alternatives review.
- The federation owns the shared ledger schema, safety floor, conventions,
  validator, example ledgers, and cross-product seam rules.

The product promise is:

> Two independent tools, one safety contract, one ledger language, no hidden
> cleanup, no cross-product code coupling, and no umbrella runtime until both
> producers independently work.

## OUTCOME

Complete Mac Tools Federation v0.1 so that both `freeup-space` and
`mac-app-audit` are represented as independent, validated federation
participants.

The completed v0.1 federation must provide:

1. A root federation contract document, preferably `FEDERATION.md`, explaining
   the two producers, their boundaries, and how ledgers cross-reference.
2. A normalized `MAC_App_Audit` federation contract layout or flat-layout
   validator/test implementation where docs, paths, and tests agree.
3. A passing `MAC_App_Audit` validator suite in the current checkout.
4. A root federation smoke test proving the shared schema and example ledger
   include both producers and at least one cross-producer seam.
5. Preserved FreeUp Space v0.2 CLI/report behavior.
6. A safe path for future work that can build `mac-app-audit v0.2` only after
   the implementation-root mismatch is resolved.
7. No cleanup execution, no app uninstall execution, no `sudo`, no daemon, no
   telemetry, and no umbrella CLI.

## Required Federation Shape

Use a file-based federation, not shared runtime code.

The canonical ledger location remains:

```text
~/.local/share/mac-tools-federation/ledgers/<producer>.ledger.json
```

Producer examples:

```text
~/.local/share/mac-tools-federation/ledgers/freeup-space.ledger.json
~/.local/share/mac-tools-federation/ledgers/mac-app-audit.ledger.json
```

Rules:

1. One producer may read another producer's ledger.
2. A producer must never write another producer's ledger.
3. Cross-product links use `related_entries` and stable `entry_id` values.
4. Missing sibling ledgers are not fatal; treat the sibling as not installed or
   not yet producing ledger entries.
5. The schema remains additive within a major version.
6. Consumers must ignore unknown fields.

## Implementation Phases

### Phase 0 - Preflight And Dirty-State Truth

Before editing, inspect and record:

```bash
git status --short --branch
find MAC_App_Audit -maxdepth 3 -type f -print | sort
```

Confirm the active facts from `MAC_App_Audit/HANDOFF_2026-07-03.md`:

- `MAC_App_Audit/` is currently flat.
- The flat validator command works.
- `test_validator.py` is path-broken.
- The mac-app-audit implementation files are absent unless newly found.
- FreeUp Space and mac-app-audit remain separate products.

Do not hide or overwrite pre-existing dirty work.

### Phase 1 - Normalize The Federation Contract Bundle

Choose the smallest safe normalization path after inspection:

Option A: keep the flat `MAC_App_Audit/` layout and update docs/tests so the
flat layout is explicit and validated.

Option B: restore the canonical federation layout inside `MAC_App_Audit/`:

```text
MAC_App_Audit/schema/ledger-entry.schema.json
MAC_App_Audit/schema/CHANGELOG.md
MAC_App_Audit/validator/validate_ledger.py
MAC_App_Audit/examples/example_ledger.json
MAC_App_Audit/tests/test_validator.py
MAC_App_Audit/tests/fixtures_invalid_ledger.json
```

Prefer Option A unless there is clear evidence the current directory should be
converted into the canonical standalone `mac-tools-federation` repo. Do not
move files destructively; use normal git-tracked edits and preserve content.

Done means the chosen layout is documented consistently and:

```bash
cd MAC_App_Audit
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 test_validator.py
```

all pass in the current checkout, or equivalent canonical-layout commands pass
if Option B is chosen and documented.

### Phase 2 - Add Root Federation Documentation

Create or update `FEDERATION.md` so a future agent can understand:

1. What the federation is and is not.
2. Why FreeUp Space and mac-app-audit stay independent.
3. Which product owns each overlap area:
   - Homebrew cache cleanup: FreeUp Space.
   - Homebrew package keep/remove recommendations: mac-app-audit.
   - Local AI model bytes: FreeUp Space.
   - Local AI runners/tools: mac-app-audit.
4. How `related_entries` links producer findings.
5. Where ledger files live.
6. How to validate a ledger.
7. Why no umbrella CLI, daemon, telemetry, install, uninstall, or cleanup
   execution is part of v0.1.
8. Current adopter status:
   - FreeUp Space has a working v0.2 CLI/report path but not a live default
     ledger writer unless implemented later.
   - `MAC_App_Audit/` currently has the federation contract bundle and a
     planned mac-app-audit v0.2 goal; app implementation starts only after
     the implementation-root mismatch is resolved.

### Phase 3 - Add Root Federation Smoke Coverage

Add `tests/test_federation_contract.py` or an equivalent narrow smoke test.

It must prove:

1. The ledger schema loads as valid JSON.
2. The bundled example ledger validates with the local validator.
3. The example ledger contains at least one `producer: mac-app-audit` entry.
4. The example ledger contains at least one `producer: freeup-space` entry.
5. At least one entry from one producer references an entry from the other
   producer via `related_entries`.
6. Root federation docs name both:
   - `/Users/o2satz/FreeUp-Space-Claude`
   - `/Users/o2satz/FreeUp-Space-Claude/MAC_App_Audit`

The test must not run live macOS audits, cleanup commands, app installs,
app uninstalls, package installs, network calls, or live ledger writes.

### Phase 4 - Preserve FreeUp Space v0.2

FreeUp Space v0.2 must continue to work after federation edits.

Run and pass:

```bash
bash -n scripts/disk_audit.sh
bash -n install.sh
bash -n uninstall.sh
python3 -m py_compile scripts/generate_report.py
python3 -m py_compile scripts/freeup_space.py
python3 tests/smoke_test.py
python3 tests/test_cli_smoke.py
python3 scripts/freeup_space.py --help
python3 scripts/freeup_space.py doctor
python3 scripts/freeup_space.py report --input tests/fixtures/sample_audit.txt --output /tmp/freeup-space-report.md
```

Do not require a live disk audit for federation completion unless explicitly
running an optional macOS-only manual smoke test. Any live audit remains
read-only.

### Phase 5 - Prepare The Next mac-app-audit Build, But Do Not Fake It

After the federation contract is normalized, update `MAC_App_Audit/GOAL.md`
only if needed so it clearly says whether:

1. `MAC_App_Audit/` is now the actual app implementation root, or
2. `MAC_App_Audit/` is a federation contract bundle and the app implementation
   root still needs to be located or created.

Do not claim `mac-app-audit v0.2` is implemented unless the missing files and
proof commands from `MAC_App_Audit/HANDOFF_v0.1.md` actually exist and pass.

## PROOF OF DONE

Run and pass:

```bash
git status --short --branch
git diff --check
```

Run the FreeUp Space validation:

```bash
bash -n scripts/disk_audit.sh
bash -n install.sh
bash -n uninstall.sh
python3 -m py_compile scripts/generate_report.py
python3 -m py_compile scripts/freeup_space.py
python3 tests/smoke_test.py
python3 tests/test_cli_smoke.py
python3 scripts/freeup_space.py --help
python3 scripts/freeup_space.py doctor
python3 scripts/freeup_space.py report --input tests/fixtures/sample_audit.txt --output /tmp/freeup-space-report.md
```

Run the federation validation:

```bash
cd MAC_App_Audit
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 test_validator.py
```

Run the root federation smoke test:

```bash
python3 tests/test_federation_contract.py
```

Also verify by file inspection:

1. `GOAL.md` names `MAC_App_Audit/HANDOFF_2026-07-03.md` as source evidence.
2. `FEDERATION.md` exists and names both producers and their boundaries.
3. The example ledger includes both `mac-app-audit` and `freeup-space`.
4. At least one cross-producer `related_entries` seam exists.
5. No source path added in this run executes cleanup, app uninstall, package
   install, `sudo`, daemon setup, telemetry, or live ledger mutation by default.
6. No `__pycache__`, temporary ledgers, generated reports, or local-only test
   outputs remain in the repo tree.
7. `git diff --stat` shows only scoped federation/doc/test changes plus any
   pre-existing FreeUp v0.2 changes that were already in the worktree.

## SCOPE

Allowed to modify:

- `GOAL.md`
- `FEDERATION.md`
- `README.md`
- `AGENTS.md`
- `tests/test_federation_contract.py`
- `MAC_App_Audit/GOAL.md`
- `MAC_App_Audit/README.md`
- `MAC_App_Audit/CONVENTIONS.md`
- `MAC_App_Audit/validate_ledger.py`
- `MAC_App_Audit/test_validator.py`
- `MAC_App_Audit/example_ledger.json`
- narrow `MAC_App_Audit` fixture files required to make validator tests pass

Allowed to read/reference:

- `MAC_App_Audit/HANDOFF_2026-07-03.md`
- `MAC_App_Audit/HANDOFF_LATEST.md`
- `MAC_App_Audit/HANDOFF_v0.1.md`
- `MAC_App_Audit/SAFETY_CONTRACT.md`
- `MAC_App_Audit/CHANGELOG.md`
- `MAC_App_Audit/ledger-entry.schema.json`
- FreeUp Space scripts, tests, docs, and current v0.2 CLI files

Avoid modifying unless direct validation requires it:

- `scripts/disk_audit.sh`
- `scripts/generate_report.py`
- `scripts/freeup_space.py`
- `install.sh`
- `uninstall.sh`
- `tests/smoke_test.py`
- `tests/test_cli_smoke.py`

Do not modify:

- user data outside this repo
- live federation ledgers under `~/.local/share/mac-tools-federation/`
- generated Desktop or `/tmp` reports except explicit test output paths
- git remotes or branches
- any production deployment surface

## CONSTRAINTS

1. Preserve the FreeUp Space safety contract: no automatic deletion, no cache
   clearing, no snapshot thinning, no hidden cleanup, and no `sudo`.
2. Preserve the federation safety contract in
   `MAC_App_Audit/SAFETY_CONTRACT.md`; do not loosen it.
3. Keep the audit/report path read-only.
4. Keep tests fixture-based and non-destructive.
5. Do not add telemetry, daemons, launch agents, background collection, or
   network calls.
6. Do not add an umbrella CLI or suite dispatcher.
7. Do not merge FreeUp Space and mac-app-audit implementation logic.
8. Do not write live ledger files during tests.
9. Do not add dependencies unless required and documented. The federation
   validator must run in a fresh clone using its standard-library fallback when
   `jsonschema` is unavailable.
10. Use the Python standard library for new tests unless an existing validator
    dependency is already required.
11. Keep macOS-specific checks graceful on Linux CI.
12. Do not remove or weaken tests to make the goal pass.

## SAFETY / PROVENANCE

- The federation is an audit and decision-record system, not an execution
  system.
- Ledger entries are evidence-bearing records, not cleanup actions.
- Recommendations without evidence must render as unverified or
  `not_assessed`, not as confident recommendations.
- User decisions such as accepted, rejected, deferred, reason, decided_at, and
  revisit_after must survive reruns once live ledger writing exists.
- FreeUp Space owns disk-space and bytes-on-disk findings.
- mac-app-audit owns tool-choice and app/software findings.
- Cross-product seams use `related_entries`; they do not use code calls,
  shared mutable runtime state, or hidden side effects.
- If a capability is planned but absent, document it as deferred or blocked
  instead of claiming it is complete.

## ITERATION

1. Start by reading the source files named in `Source Of Truth`, especially
   `MAC_App_Audit/HANDOFF_2026-07-03.md`.
2. Establish the current baseline with the validation commands that can run
   before edits.
3. Fix the smallest hard blocker first: `MAC_App_Audit/test_validator.py` path
   and fixture assumptions.
4. Add or update federation docs only after the chosen layout is clear.
5. Add root smoke coverage after docs and validator behavior agree.
6. Re-run the nearest relevant verification after each batch.
7. Keep a concise progress record in the final summary unless `PROGRESS.md`
   exists and is already used by this repo.
8. Preserve all unrelated dirty work.

## STOP

Pause and summarize before continuing if:

1. `MAC_App_Audit/` cannot be classified as either a contract bundle or app
   implementation root after inspection.
2. The federation validator cannot validate the bundled example ledger using
   either `jsonschema` or the standard-library fallback.
3. The same failure persists after three distinct repair attempts.
4. The implementation would require cleanup execution, app uninstall execution,
   `sudo`, live ledger mutation, package installation, telemetry, daemon setup,
   production deployment, or network access.
5. Completing the work would require changing the shared schema in a
   non-additive way.
6. A product decision would materially change the ownership boundary between
   FreeUp Space and mac-app-audit.

## COMPLETE

Mark this goal complete only when:

1. `GOAL.md` has been updated from `MAC_App_Audit/HANDOFF_2026-07-03.md`.
2. The federation contract is documented at the root.
3. The `MAC_App_Audit` validator suite passes in the current layout.
4. The root federation smoke test passes.
5. FreeUp Space v0.2 validation still passes.
6. Safety contracts remain intact and no cleanup execution is introduced.
7. The implementation-root truth for mac-app-audit is explicitly documented.
8. `git diff --check` is clean.
9. Generated caches and local-only artifacts are absent from the repo tree.
10. The final summary separates verified behavior from deferred future work.

Do not push unless the user explicitly asks.
