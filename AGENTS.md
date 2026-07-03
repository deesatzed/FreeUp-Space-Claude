# AGENTS.md

## Project Role

This repository contains a macOS disk cleanup skill and standalone audit/reporting scripts. The assistant should act as a cautious macOS storage analyst, not as an aggressive cleanup bot.

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
- `FEDERATION.md`: file-based federation contract between FreeUp Space and mac-app-audit.
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
python3 -m py_compile scripts/generate_report.py
python3 -m py_compile scripts/freeup_space.py
python3 tests/smoke_test.py
python3 tests/test_cli_smoke.py
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
python3 scripts/freeup_space.py report --input tests/fixtures/sample_audit.txt --output /tmp/freeup-space-report.md
```

On macOS only, a live manual smoke test is:

```bash
bash scripts/disk_audit.sh /tmp/freeup-space-audit.txt
python3 scripts/generate_report.py /tmp/freeup-space-audit.txt /tmp/freeup-space-report.md
open /tmp/freeup-space-report.md
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

The highest-value future improvement is to convert the loose text audit into structured JSON while preserving a readable text fallback. That would let reports rank findings more accurately, power UI output, and reduce fragile parsing.
