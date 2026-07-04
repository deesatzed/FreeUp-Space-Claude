# GOAL_Public_READINESS.md - Historical CLI Hardening Contract

> Correction, 2026-07-04: this file is retained as evidence for CLI/report
> hardening. It is not the current product-readiness contract. The current
> readiness goal is `GOAL_AGENT_NATIVE_READINESS.md`, where Codex or Claude
> Code is the manager and skills/commands are the primary invocation surfaces.

Use this file from the repository root with:

```text
/goal GOAL_Public_READINESS.md
```

## Source Of Truth

This goal is grounded in the current checkout of FreeUp Space and the real
non-smoke test run performed on 2026-07-04.

Before editing, read these files if present:

1. `AGENTS.md`
2. `GOAL.md`
3. `GOAL_TEST_CLONE.md`
4. `README.md`
5. `FEDERATION.md`
6. `SKILL.md`
7. `scripts/freeup_space.py`
8. `scripts/generate_report.py`
9. `scripts/disk_audit.sh`
10. `install.sh`
11. `uninstall.sh`
12. `tests/smoke_test.py`
13. `tests/test_cli_smoke.py`
14. `tests/test_federation_contract.py`
15. `MAC_App_Audit/README.md`
16. `MAC_App_Audit/SAFETY_CONTRACT.md`
17. `MAC_App_Audit/CONVENTIONS.md`

## Current Real-Test Findings To Mitigate

The 2026-07-04 real functional test proved that the app can run real live
audits and produce useful reports. It also found public-readiness gaps that
must be mitigated before claiming the app is ready for a public audience.

Observed working surfaces:

1. `python3 scripts/freeup_space.py --help` lists `audit`, `report`, `doctor`,
   `dev`, `models`, and `plan`.
2. `audit --output /tmp/...` runs a real read-only macOS audit and writes a
   detailed audit text file.
3. `report --input ... --output ...` generates a Markdown report with disk
   overview, top findings, cache findings, application sizes, audit coverage,
   and advisory command suggestions.
4. `plan --input ...` prints top findings and advisory command text without
   executing cleanup.
5. `dev` and `models` run the same safe audit/report path with mode-specific
   introductory text.
6. The no-argument workflow runs the default audit/report path and writes to
   Desktop.
7. The installer/uninstaller work under a temporary `HOME`.
8. The federation validator and smoke test pass, including in a fresh clone
   without `jsonschema`.

Observed public-readiness issues:

1. The no-argument default workflow cannot accept `--no-open`,
   `--audit-output`, `--report-output`, or `--non-interactive`, so users must
   know subcommands to control output/opening behavior.
2. Full-flow output order is confusing: subprocess output such as
   `Report saved...` can appear before the FreeUp Space banner and mode
   explanation.
3. The report and plan use the heading `Quick Cleanup Commands`, which is too
   action-oriented for a safety-first public app.
4. The cache heading `Top Caches (Safe to Clear)` is too confident. Caches are
   lower risk, not automatically safe for every user or app state.
5. The report and plan show raw command text including commands such as
   `rm -rf ".../Library/Caches/ms-playwright"`. This remains advisory text, but
   the UI/copy must make the non-execution and approval boundary harder to
   miss.
6. The disk overview can confuse public users because `df -h /` reports the
   sealed system volume while APFS/Data volume and user-directory findings show
   the larger real storage picture.
7. Long live audits can run for roughly a minute or more with little progress
   detail after startup, which makes the workflow feel stalled.
8. `dev` and `models` modes currently behave mostly as labeled aliases for the
   same audit/report path. Public copy must make that explicit or add real
   mode-specific value.
9. Public readiness needs a repeatable non-smoke verification script or
   documented test checklist that exercises every public feature in detail
   without executing cleanup.

## OUTCOME

Bring FreeUp Space to a public-readiness status by mitigating every issue above
while preserving the core promise:

> Find reclaimable space, explain it clearly, and never delete anything without
> explicit approval.

Done means a public user can run the app, understand what it is doing, inspect
real results in detail, distinguish lower-risk caches from judgment-required
data, and see advisory command text without any hidden cleanup execution.

## PROOF OF DONE

Run from the repository root.

### 1. Preflight And Dirty-State Truth

```bash
pwd
git status --short --branch
git remote -v
git rev-parse HEAD
```

Confirm:

- The current checkout is the intended FreeUp Space repo.
- Any pre-existing dirty work is identified before edits.
- Existing user changes are preserved.

### 2. Public CLI Surface

Run:

```bash
python3 scripts/freeup_space.py --help
python3 scripts/freeup_space.py audit --help
python3 scripts/freeup_space.py report --help
python3 scripts/freeup_space.py doctor --help
python3 scripts/freeup_space.py plan --help
python3 scripts/freeup_space.py dev --help
python3 scripts/freeup_space.py models --help
```

Confirm:

- The default/no-command workflow exposes documented controls for output paths,
  non-interactive mode, and report opening, either directly on the root parser
  or through a clearly documented `run`/equivalent command.
- Help text says audit/report/plan output is advisory and non-destructive.
- `dev` and `models` help text clearly states whether these modes are aliases
  with mode-specific framing or provide additional mode-specific checks.
- Help text does not imply cleanup is executed by default.

### 3. Default Workflow Control

Run a real workflow with explicit output paths and no automatic opening:

```bash
python3 scripts/freeup_space.py \
  --audit-output /tmp/freeup-public-default-audit.txt \
  --report-output /tmp/freeup-public-default-report.md \
  --no-open \
  --non-interactive
test -s /tmp/freeup-public-default-audit.txt
test -s /tmp/freeup-public-default-report.md
```

If the final design chooses an explicit `run` subcommand instead of root-level
options, use the documented equivalent command and update this goal file before
claiming completion.

Confirm:

- The default workflow no longer forces Desktop output when explicit output
  paths are supplied.
- The workflow can be non-interactive for CI/manual verification.
- The workflow can avoid opening the report.
- The output order begins with the FreeUp Space banner/mode explanation before
  subprocess status lines.
- No cleanup commands are executed.

### 4. Individual Feature Workflows

Run:

```bash
python3 scripts/freeup_space.py doctor
python3 scripts/freeup_space.py audit --output /tmp/freeup-public-audit.txt
python3 scripts/freeup_space.py report --input /tmp/freeup-public-audit.txt --output /tmp/freeup-public-report.md
python3 scripts/freeup_space.py plan --input /tmp/freeup-public-audit.txt
python3 scripts/freeup_space.py plan --input /tmp/freeup-public-audit.txt --output /tmp/freeup-public-plan-report.md
python3 scripts/freeup_space.py dev --audit-output /tmp/freeup-public-dev-audit.txt --report-output /tmp/freeup-public-dev-report.md --no-open --non-interactive
python3 scripts/freeup_space.py models --audit-output /tmp/freeup-public-models-audit.txt --report-output /tmp/freeup-public-models-report.md --no-open --non-interactive
```

Confirm:

- Every command exits 0 on macOS.
- All generated audit/report paths are non-empty.
- `doctor` reports required runtime dependencies and macOS live-audit tools.
- `plan` prints detailed findings and advisory action text without executing
  actions.
- `dev` and `models` either provide useful mode-specific details or clearly
  state that v0.2 uses the shared safe audit/report path.
- Long-running live audit commands provide enough progress/status output that a
  user can tell the app is still working.

### 5. Report Content And UX Copy

Inspect the real generated report:

```bash
sed -n '1,240p' /tmp/freeup-public-report.md
rg -n "Quick Cleanup Commands|Safe to Clear|rm -rf|sudo|Command Suggestions|not executed|approval|APFS|Data volume|sealed system" /tmp/freeup-public-report.md
```

Confirm:

- The report has clear sections for disk overview, top findings, caches,
  applications, audit coverage, and advisory actions.
- The report explains the macOS APFS/system/Data-volume distinction in plain
  language when disk overview data is shown.
- The report does not use `Top Caches (Safe to Clear)` or other wording that
  implies automatic safety.
- The report does not use `Quick Cleanup Commands` as the primary heading.
  Prefer wording like `Command Suggestions: Review Before Running` or
  `Manual Action Suggestions`.
- Any command text, including `rm -rf` or `sudo` examples, is clearly labeled
  as not executed and requiring explicit user approval.
- User data, cloud sync folders, app support data, applications, photos,
  videos, documents, downloads, and project folders remain judgment-required.
- The report recommends moving/archiving user data when uncertain.

### 6. Plan Output UX Copy

Run and inspect:

```bash
python3 scripts/freeup_space.py plan --input /tmp/freeup-public-audit.txt > /tmp/freeup-public-plan-output.txt
sed -n '1,220p' /tmp/freeup-public-plan-output.txt
rg -n "Quick Cleanup Commands|Safe to Clear|rm -rf|sudo|not executed|approval|review" /tmp/freeup-public-plan-output.txt
```

Confirm:

- The plan output uses the same safety vocabulary as the report.
- It clearly separates findings from advisory command text.
- It never says a command was run.
- It does not make cache clearing sound automatic or universally safe.

### 7. Fixture Tests And Public-Readiness Regression Coverage

Add or update focused tests so the public-readiness issues are not reintroduced.

Run:

```bash
bash -n scripts/disk_audit.sh
bash -n install.sh
bash -n uninstall.sh
python3 -m py_compile scripts/generate_report.py
python3 -m py_compile scripts/freeup_space.py
python3 tests/smoke_test.py
python3 tests/test_cli_smoke.py
python3 tests/test_federation_contract.py
```

If a new public-readiness test file is added, run it explicitly, for example:

```bash
python3 tests/test_public_readiness.py
```

Confirm the tests cover at least:

- Root/default workflow options or the chosen explicit run command.
- Safer report headings.
- Safer plan headings/copy.
- Parent output ordering or flushing behavior.
- Missing-input errors for `report` and `plan`.
- The installer/uninstaller still operate only under the intended wrapper path.

### 8. Sandboxed Installed Wrapper

Run:

```bash
TMP_HOME="$(mktemp -d)"
mkdir -p "$TMP_HOME/Desktop"
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" bash install.sh
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" freeup-space --help
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" freeup-space doctor
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" freeup-space report --input tests/fixtures/sample_audit.txt --output /tmp/freeup-public-wrapper-report.md
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" freeup-space plan --input tests/fixtures/sample_audit.txt > /tmp/freeup-public-wrapper-plan.txt
test -s /tmp/freeup-public-wrapper-report.md
test -s /tmp/freeup-public-wrapper-plan.txt
HOME="$TMP_HOME" PATH="$TMP_HOME/.local/bin:$PATH" bash uninstall.sh
test ! -e "$TMP_HOME/.local/bin/freeup-space"
rm -rf "$TMP_HOME"
```

Confirm:

- The wrapper is installed only under the temporary `HOME`.
- The wrapper can run help, doctor, report, and plan.
- The uninstaller removes only the temporary wrapper.
- No real user install path is modified.

### 9. Federation Non-Regression

Run:

```bash
cd MAC_App_Audit
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 validate_ledger.py example_ledger.json
python3 test_validator.py
cd ..
python3 tests/test_federation_contract.py
```

Confirm:

- The flat `MAC_App_Audit` validator bundle still works.
- The federation smoke test still proves both producers and a cross-producer
  seam.
- Public-readiness changes do not create an umbrella runtime, daemon, or shared
  cleanup executor.

### 10. Public Documentation

Update docs where needed:

- `README.md`
- `SKILL.md`
- `AGENTS.md` only if workflow or validation commands change
- Any relevant test or fixture documentation

Confirm by inspection:

- The quickstart accurately reflects the public CLI after changes.
- The docs show how to run a controlled output/no-open workflow.
- The docs explain that advisory commands are not executed.
- The docs explain how to inspect generated reports.
- The docs avoid claiming public readiness until all proof gates pass.

### 11. Final Safety And Artifact Checks

Run:

```bash
find . \( -name __pycache__ -o -name '*.pyc' -o -name '*freeup-public-*' \) -print
rg -n "sudo|rm -rf|trash|brew uninstall|pip install|launchd|daemon|telemetry|live ledger|cleanup command|app uninstall" FEDERATION.md AGENTS.md README.md SKILL.md scripts tests MAC_App_Audit
git diff --check
git status --short --branch
```

Confirm:

- Repo-local generated bytecode and public-readiness temp artifacts are removed
  before completion.
- Any `rg` hits are safety documentation, inert recommendation text, tests, or
  explicit non-execution copy.
- No default runtime path executes cleanup, app uninstall, package install,
  telemetry, daemon setup, `sudo`, or live ledger writes.
- The final dirty tree contains only intentional public-readiness edits.

## SCOPE

Allowed to modify:

- `scripts/freeup_space.py`
- `scripts/generate_report.py`
- `tests/`
- `README.md`
- `SKILL.md`
- `AGENTS.md` only if validation commands or operating instructions change
- `GOAL_Public_READINESS.md` if the implementation path changes and the goal
  must stay accurate

Allowed to read/reference:

- `AGENTS.md`
- `GOAL.md`
- `GOAL_TEST_CLONE.md`
- `FEDERATION.md`
- `references/safe-cleanup-targets.md`
- `MAC_App_Audit/` contract files
- Real audit/report outputs under `/tmp` or explicitly chosen output paths

Do not modify:

- Live user ledgers under `~/.local/share/mac-tools-federation/`
- The user's real `~/.local/bin/freeup-space`
- User data outside explicitly generated audit/report files
- Git remotes, deployment settings, or release metadata
- `MAC_App_Audit` implementation scope beyond non-regression validation

## CONSTRAINTS

1. Preserve the safety contract: no deletion, moving, cache clearing, snapshot
   thinning, app uninstall, package install, migration, telemetry, daemon setup,
   `sudo`, or live ledger writes during tests or default operation.
2. Keep the audit path read-only.
3. Use Python standard library only unless a dependency is already present and
   clearly justified.
4. Keep shell scripts Bash 3.2/macOS compatible.
5. Keep report parsing tolerant of missing sections and partial audit data.
6. Do not weaken safety copy or tests to make public-readiness checks pass.
7. Do not remove command suggestions entirely unless a better public-safe
   replacement still helps users understand the next manual action.
8. Do not hide uncertainty. If a target is judgment-required, say so.
9. Do not invent reclaimable-space totals beyond measured findings.
10. Do not implement cleanup execution. Public readiness here is audit, report,
    planning text, and workflow clarity only.

## SAFETY / PROVENANCE

- All cleanup/action command text is advisory documentation until a future,
  separate, explicitly approved execution goal exists.
- Command suggestions must show why they appear and what evidence from the
  audit supports them.
- Caches are lower risk, not risk-free.
- User data and app state require review, moving, archiving, or app-native
  management before deletion.
- Missing, skipped, or unreadable audit checks must remain visible in the
  report and must not be treated as zero usage.
- Public-readiness claims must distinguish fixture evidence from live macOS
  evidence.
- Federation entries are decision records, not cleanup actions.

## ITERATION

1. Start with a fresh repo-state audit and record dirty-state truth.
2. Turn the observed public-readiness issues into a small implementation
   checklist.
3. Add or update the nearest focused regression test before changing behavior
   when practical.
4. Make one small change batch at a time:
   - default workflow controls,
   - output-order/flush behavior,
   - report wording,
   - plan wording,
   - APFS/Data-volume explanation,
   - progress/status visibility,
   - docs/tests.
5. After each batch, run the nearest relevant verification command.
6. If a live macOS audit is slow, continue polling rather than replacing it
   with fixture evidence for public-readiness proof.
7. Keep generated audit/report artifacts under `/tmp` unless intentionally
   testing Desktop defaults.
8. Remove repo-local `__pycache__` and `.pyc` artifacts before final status.
9. End with a requirement-by-requirement completion audit against this file.

## STOP

Stop and summarize if:

- A requested verification command would execute cleanup, app uninstall,
  package install, telemetry, daemon setup, `sudo`, or live ledger mutation.
- A change would require a product decision about whether to remove command
  suggestions entirely rather than making them safer and clearer.
- A live audit repeatedly fails for environmental reasons after three distinct
  mitigation attempts.
- The implementation requires modifying user data outside generated audit/report
  outputs.
- The federation validator cannot validate the bundled example ledger using
  either `jsonschema` or the standard-library fallback.
- The same test failure persists after three distinct repair attempts.
- The work would require a broader app-audit implementation or a shared umbrella
  runtime.

## COMPLETE

Mark complete only when:

1. Every issue listed under `Current Real-Test Findings To Mitigate` has a
   concrete mitigation in code, docs, tests, or an explicit documented deferral
   with rationale.
2. All `PROOF OF DONE` command groups pass with current command output.
3. A real macOS live audit/report/plan workflow has been run after the final
   edits.
4. The report and plan use public-safe advisory wording and preserve clear
   approval boundaries.
5. Default or run workflow output paths/open behavior are controllable from the
   public CLI.
6. Fixture tests and at least one public-readiness regression check cover the
   mitigated issues.
7. Federation validation still passes.
8. No cleanup, app uninstall, package install, telemetry, daemon setup, `sudo`,
   or live ledger write occurred.
9. Repo-local generated artifacts are removed.
10. The final summary separates:
    - required fixture/CI proof,
    - required live macOS proof,
    - remaining deferred future work,
    - exact files changed.
