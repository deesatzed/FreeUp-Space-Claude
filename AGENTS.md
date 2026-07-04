# AGENTS.md

## Project Role

This repository contains Codex/Claude-native macOS storage and app-audit
surfaces. The primary product surface is skills and command markdown managed by
Codex or Claude Code. Bash/Python CLIs are deterministic read-only helper
scripts for audit, reporting, tests, and repeatability; do not treat them as a
standalone cleanup app.

The product promise is simple: **find reclaimable space, explain it clearly, and never delete anything without explicit approval.**

## Safety Contract

These rules are mandatory for all future Codex work in this repository:

1. Do not add code that deletes, moves, thins snapshots, clears caches, or runs `sudo` without a separate explicit user approval step.
2. Keep the audit path read-only.
3. Tests and CI must never execute destructive cleanup commands.
4. Prefer reporting and recommendation over automatic action.
5. Treat caches as lower risk, but still show commands before execution.
6. Treat user data, cloud sync folders, photos, videos, documents, and project folders as judgment-required.
7. When unsure, recommend moving to an external drive rather than deleting.
8. Keep macOS-specific logic graceful when run on Linux CI.

## Repository Map

- `SKILL.md`: Claude skill instructions and behavioral workflow.
- `README.md`: human-facing overview and installation/use instructions.
- `GOAL.md`: project goal and implementation handoff.
- `GOAL_AGENT_NATIVE_READINESS.md`: current Codex/Claude-native readiness goal.
- `FEDERATION.md`: file-based federation contract between FreeUp Space and mac-app-audit.
- `agent_surfaces/`: installable Codex/Claude skill and command surfaces.
- `install.sh`: no-sudo installer for the `freeup-space` wrapper.
- `uninstall.sh`: removes only the installed wrapper.
- `MAC_App_Audit/`: flat federation contract bundle and planned mac-app-audit goal.
- `codex/tasks.md`: task packs for Codex.
- `scripts/disk_audit.sh`: read-only macOS disk audit.
- `scripts/freeup_space.py`: user-facing CLI wrapper.
- `scripts/generate_report.py`: audit-to-Markdown report generator.
- `references/safe-cleanup-targets.md`: cleanup knowledge base.
- `evals/evals.json`: skill evaluation scenarios.
- `tests/smoke_test.py`: cross-platform smoke test for report generation.
- `tests/test_cli_smoke.py`: fixture-based CLI and installer smoke test.
- `tests/test_federation_contract.py`: fixture-based federation contract smoke test.

## Validation Commands

Run these before summarizing changes when editing scripts, docs that mention commands, or report output:

```bash
bash -n scripts/disk_audit.sh
bash -n install.sh
bash -n uninstall.sh
bash -n scripts/install_agent_surfaces.sh
python3 -m py_compile scripts/generate_report.py
python3 -m py_compile scripts/freeup_space.py
python3 tests/smoke_test.py
python3 tests/test_cli_smoke.py
python3 tests/test_public_readiness.py
python3 tests/test_agent_surfaces.py
python3 tests/test_federation_contract.py
```

When editing federation docs or `MAC_App_Audit/`, also run:

```bash
cd MAC_App_Audit
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 test_validator.py
cd ..
```

When editing the v0.2 CLI surface, also smoke these direct commands:

```bash
python3 scripts/freeup_space.py --help
python3 scripts/freeup_space.py doctor
python3 scripts/freeup_space.py --audit-output /tmp/freeup-space-audit.txt --report-output /tmp/freeup-space-report.md --no-open --non-interactive
python3 scripts/freeup_space.py report --input tests/fixtures/sample_audit.txt --output /tmp/freeup-space-report.md
```

On macOS only, a live manual smoke test is:

```bash
bash scripts/disk_audit.sh /tmp/freeup-space-audit.txt
python3 scripts/generate_report.py /tmp/freeup-space-audit.txt /tmp/freeup-space-report.md
python3 scripts/freeup_space.py plan --input /tmp/freeup-space-audit.txt
```

Do not run cleanup commands during validation.

## Coding Standards

### Shell

- Keep `disk_audit.sh` POSIX-ish/Bash 3.2 compatible for stock macOS.
- Use quoted variables for paths.
- Paths with spaces must work.
- Missing optional directories or tools should be reported, not fatal.
- Avoid `find` across the full home directory unless the user explicitly asks; it is slow and permission-noisy.

### Python

- Use the Python standard library only unless there is a strong reason to add dependencies.
- Keep parsing tolerant of missing sections.
- Report generation should continue with partial audit data.
- Avoid machine-specific assumptions in tests.

### Documentation

- Commands must be copy-pasteable.
- Separate safe cache actions from user-judgment actions.
- Explain why a target is safe or risky.
- Keep the user-facing language calm, direct, and non-alarmist.

## Desired Future Direction

The highest-value future improvement is to keep the agent-native surface honest:
Codex/Claude skills and commands should route the work, while deterministic
helpers produce structured data. Converting the loose text audit into
structured JSON remains valuable because it would make agent summaries and
reports less parser-fragile.
