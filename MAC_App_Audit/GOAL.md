# GOAL.md - mac-app-audit v0.2

Source evidence read while shaping this goal:

- `HANDOFF_v0.1.md`
- `README.md`
- `SAFETY_CONTRACT.md`
- `CONVENTIONS.md`
- `CHANGELOG.md`
- `ledger-entry.schema.json`
- `example_ledger.json`
- `validate_ledger.py`
- `test_validator.py`
- `/Users/o2satz/FreeUp-Space-Claude/AGENTS.md`
- `/Users/o2satz/FreeUp-Space-Claude/GOAL.md`
- `/Users/o2satz/FreeUp-Space-Claude/README.md`
- `/Users/o2satz/FreeUp-Space-Claude/SKILL.md`

Task type: multi-phase build with safety/provenance constraints.

Raw objective: convert `mac-app-audit` from a working skill prototype into a ledger-native, periodically run Mac software audit tool that keeps the audit path read-only, computes deterministic usage signals, writes federation-valid ledger entries, and supports a short weekly delta mode.

Important repo-placement note: the handoff describes an implementation repo containing `SKILL.md`, `scripts/collect_inventory.sh`, `commands/audit-apps.md`, and sample inventory fixtures. If those files are absent in the active working directory, do not treat federation contract files as a substitute implementation target. Locate the actual `mac-app-audit` implementation root or stop with a concise mismatch report before editing.

Workspace/federation note observed on 2026-07-03: this directory currently lives at `/Users/o2satz/FreeUp-Space-Claude/MAC_App_Audit`, inside the active FreeUp Space checkout. The parent `/Users/o2satz/FreeUp-Space-Claude` project is itself being completed as FreeUp Space v0.2 and is intended to become a separate producer in the same final file-based federation. Treat that parent project as live sibling-product context, not as mac-app-audit implementation code. The two tools may coordinate only through the shared federation contract and future ledger `related_entries`; do not copy, merge, or fork FreeUp Space cleanup logic into mac-app-audit.

```text
/goal
OUTCOME:
Build mac-app-audit v0.2 - Ledger-Native Collector + Deterministic Scoring + Delta Mode - so that the actual mac-app-audit implementation repo can:
1. collect deterministic usage signals for apps and Homebrew tools,
2. derive CLI invocation counts from retroactive local shell-history reads,
3. compute Homebrew dependency leaf/dependent signals,
4. write valid mac-tools-federation ledger entries,
5. read prior ledger decisions so rejected-with-reason findings suppress repeated suggestions,
6. produce a short weekly --delta briefing, and
7. prove the pipeline with fixture-based tests that do not require a live Mac or execute cleanup actions.

PROOF OF DONE:
1. Preflight confirms the active implementation root contains `SKILL.md`, `README.md`, `scripts/collect_inventory.sh`, and `commands/audit-apps.md`, and that the federation contract is available either as a sibling repo at `../mac-tools-federation/` or as an explicitly documented local contract bundle containing `SAFETY_CONTRACT.md`, `CONVENTIONS.md`, `ledger-entry.schema.json`, and `validate_ledger.py`. If the implementation root is absent, stop before implementation and report the mismatch instead of building inside the parent FreeUp Space app.
2. Preflight records the observed FreeUp Space relationship: `/Users/o2satz/FreeUp-Space-Claude` is an active, dirty, separately scoped storage-audit product that will later join the same federation. Confirm mac-app-audit changes do not modify FreeUp Space files except by separately authorized task scope.
3. Run initial validation before editing and record the result:
   - `bash -n scripts/collect_inventory.sh`
   - `python3 -m py_compile` for any existing Python scripts in scope
   - the current smoke or fixture tests if present
4. Implement or update the deterministic collection layer and verify:
   - `bash -n scripts/collect_inventory.sh`
   - `bash -n scripts/collect_usage_signals.sh` if that file is added
5. Implement the ledger writer and verify:
   - `python3 -m py_compile scripts/write_ledger.py`
   - `python3 scripts/write_ledger.py --input tests/fixtures/sample_inventory.json --output /tmp/mac-app-audit-test.ledger.json`
   - run the federation validator against `/tmp/mac-app-audit-test.ledger.json` using the documented local contract path for this checkout:
     - if a sibling federation checkout exists, run `python3 ../mac-tools-federation/validator/validate_ledger.py /tmp/mac-app-audit-test.ledger.json`
     - if using the flat local contract bundle observed in this directory, run `python3 validate_ledger.py /tmp/mac-app-audit-test.ledger.json --schema ledger-entry.schema.json`
6. Add or update fixture tests and verify:
   - `python3 -m py_compile tests/test_ledger_pipeline.py`
   - `python3 tests/test_ledger_pipeline.py`
7. Confirm the generated test ledger contains schema-valid entries for all verdict types represented by `tests/fixtures/sample_inventory.json`, uses producer `mac-app-audit`, and derives `entry_id` as `sha256(producer + ":" + subject.identifier)[:16]`, falling back to `subject.name` only when no stable identifier exists.
8. Confirm rerunning the ledger writer on unchanged fixture input preserves stable `entry_id` values and does not duplicate entries; only time-sensitive fields such as `updated_at` may change.
9. Inspect the --delta behavior and confirm it reads the existing ledger, detects new installs, resurfaces deferred entries whose `revisit_after` has arrived, and rotates exactly 5 stale alternatives-check candidates without performing a full recategorization pass.
10. Confirm rejected ledger entries with `decision.status: rejected` and a non-empty `decision.reason` suppress re-suggestion of the same class of change for that subject on subsequent runs unless materially new evidence is present.
11. Confirm no tests execute destructive cleanup, removal, installation, `sudo`, `brew uninstall`, `trash`, or migration commands. Recommendation text may show commands only as inert report content.
12. Run `git diff --check` and `git diff --stat`.
13. Remove `__pycache__`, temporary files, and generated local ledgers from the repo tree.
14. If local commits are authorized for this run, commit only after every proof item passes, using:
    `Add ledger-native collector, deterministic usage scoring, and delta mode`
    Do not push.

SCOPE:
- Modify only the actual mac-app-audit implementation files needed for v0.2:
  - `SKILL.md`
  - `README.md`
  - `commands/audit-apps.md` or a clearly named delta command file
  - `scripts/collect_inventory.sh`
  - `scripts/collect_usage_signals.sh` if added
  - `scripts/write_ledger.py`
  - `scripts/user_stack_profile.json` or the repo's matching config format
  - `tests/fixtures/sample_inventory.json`
  - `tests/test_ledger_pipeline.py`
  - narrowly related test fixtures or docs needed to prove the above
- Read/reference:
  - `HANDOFF_v0.1.md`
  - `/Users/o2satz/FreeUp-Space-Claude/AGENTS.md`
  - `/Users/o2satz/FreeUp-Space-Claude/GOAL.md`
  - `/Users/o2satz/FreeUp-Space-Claude/README.md`
  - `../mac-tools-federation/README.md`
  - `../mac-tools-federation/SAFETY_CONTRACT.md`
  - `../mac-tools-federation/CONVENTIONS.md`
  - `../mac-tools-federation/schema/ledger-entry.schema.json`
  - `../mac-tools-federation/schema/CHANGELOG.md`
  - `../mac-tools-federation/examples/example_ledger.json`
  - local federation contract files in this directory when no sibling `../mac-tools-federation/` checkout exists
  - existing fixture inventory/report data, including `tests/fixtures/mac_apps_report.txt` if present
- Do not modify:
  - the mac-tools-federation contract, schema, validator, examples, or changelog
  - FreeUp Space implementation files in `/Users/o2satz/FreeUp-Space-Claude` unless a separate user request explicitly scopes that work
  - unrelated project docs or generated artifacts
  - user shell-history files or live ledger files except through explicit read-only fixture-safe tests

CONSTRAINTS:
- Preserve the audit path as read-only. Do not add deletion, moving, cache clearing, snapshot thinning, installation, migration, or `sudo` behavior.
- Preserve `scripts/collect_inventory.sh` output compatibility unless the change is additive and documented.
- Keep macOS-specific behavior graceful on Linux CI. Fixture tests must not require Homebrew, Spotlight, `mdls`, real shell history, or a live Mac.
- Use shell/Bash 3.2-compatible patterns for macOS shell scripts and quote all path variables.
- Use Python standard library only unless a dependency is already required by the federation validator and the need is documented.
- Deterministic scripts own arithmetic, usage counts, dependency graph signals, entry-id derivation, ledger merging, and schema validation.
- Codex/Claude may own classification prose, redundancy-cluster reasoning, alternatives research, and report wording, but must not invent numeric confidence from vibes.
- Shell history parsing must be retroactive and local. Do not add daemons, launchd jobs, telemetry, background collection, or continuous monitoring.
- Never send raw shell history, secrets, private paths, credentials, or sensitive local command text to a web search or model prompt. Derive local counts first, then use aggregated signals.
- Alternatives research is recommend-only. It may cite current sources and migration cost, but must never install, migrate, uninstall, or alter tools.
- Seed `user_stack_profile` from the handoff's known context: Apple Silicon/Mac Mini M4, 64GB unified memory, MLX/local-inference-heavy tooling, Python/SQL/React, and AI/ML production development. Keep it editable config, not hardcoded logic.
- Keep the four-verdict taxonomy and federation schema mapping intact: `keep`, `redundant`, `superseded`, `investigate`, plus categorical `do_not_touch` where appropriate. Use existing schema enum values when ledger output needs additional nuance.
- Implement concrete starting redundancy clusters from the handoff: archive tools, file managers, markdown editors, local-inference runners, and Python version-management tools.
- Do not build Level 3 execution, an umbrella FreeUp/mac-app dispatcher, a GUI, daemon, launchd job, or federation schema 2.0 changes.
- Do not weaken, delete, or skip tests to make the goal pass.

SAFETY / PROVENANCE:
- Inherit `mac-tools-federation/SAFETY_CONTRACT.md` without loosening it.
- Preserve the final-federation boundary: mac-app-audit owns software-choice recommendations; FreeUp Space owns disk-space findings. Overlap areas such as Homebrew and local AI models must be represented by ledger references, not shared cleanup/application logic.
- Default posture is Level 1 audit + report. Level 2 may show exact commands as text only. Level 3 execution is out of scope.
- Ledger writes are passive records of analysis, not cleanup actions.
- Every non-`not_assessed` ledger entry must carry evidence or a confidence basis allowed by `ledger-entry.schema.json`.
- Web-search-backed alternatives must include citation metadata and fetched timestamps; recommendations without bounded-recent evidence render as unverified.
- Preserve user decision provenance: accepted/rejected/deferred status, reason, decided_at, and revisit_after must survive reruns.
- When uncertain, emit `investigate`, `judgment_required`, or `do_not_touch` rather than forcing a cleanup recommendation.

ITERATION:
1. Before editing, reconcile the active repo root against the handoff and the observed `/Users/o2satz/FreeUp-Space-Claude` parent. If the current directory is only the federation contract bundle or a misplaced copy of federation files, stop and report the mismatch. If the needed FreeUp Space state is relevant, inspect it read-only and keep its dirty worktree changes intact.
2. Run the nearest existing validation to establish baseline truth before changes.
3. Implement in small batches:
   - usage-signal collection,
   - ledger writer and schema validation,
   - fixture pipeline test,
   - delta mode,
   - SKILL/command/README updates,
   - rejection suppression and redundancy-cluster coverage.
4. After each batch, run the nearest verification command and fix failures before expanding scope.
5. Keep a concise progress log of changed files, commands run, failures, fixes, and remaining risks in `PROGRESS.md` if that file exists; otherwise include it in the final summary.
6. Prefer the smallest implementation that proves the contract. Defer attractive adjacent work rather than partially implementing it.

STOP:
Stop and summarize before editing if the actual mac-app-audit implementation files cannot be found.
Stop if the required federation schema/validator is unavailable and cannot be referenced without modifying the federation repo.
Stop if a required proof command cannot be run after reasonable local mitigation.
Stop if the same failure persists after 3 distinct repair attempts.
Stop if implementation would require destructive actions, `sudo`, package installs, live ledger mutation, raw shell-history disclosure, or production deployment.
Stop if the needed change would require modifying the federation schema, building an umbrella command, adding a daemon, or changing Level 3 execution scope.
Stop if a product decision would materially change the v0.2 scope described in `HANDOFF_v0.1.md`.

COMPLETE:
Mark complete only when every PROOF OF DONE item has passed using actual command output or explicit file inspection evidence, the final diff is scoped to v0.2, `git diff --check` is clean, no destructive behavior exists in tests or default runtime paths, and the final summary separates verified behavior from deferred future work.
```

Assumptions:

- `HANDOFF_v0.1.md` is the authoritative v0.2 implementation brief.
- The current directory may not be the final implementation root; the goal therefore makes repo-root reconciliation the first proof gate.
- `/Users/o2satz/FreeUp-Space-Claude` is an active FreeUp Space project and future federation participant; treat it as read-only context for mac-app-audit unless separately authorized.
- The federation contract remains read-only input for this goal.
