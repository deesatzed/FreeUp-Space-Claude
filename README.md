# FreeUp Space - Mac Storage Assistant

A Claude/Codex-friendly macOS storage assistant that performs read-only disk analysis, identifies reclaimable space, and provides prioritized cleanup recommendations. It never deletes, moves, clears caches, thins snapshots, or runs `sudo` in v0.2.

## What It Does

- **Full disk audit**: APFS volumes, Time Machine snapshots, app caches, dev tool caches, cloud sync overhead
- **Smart questioning**: Asks about your setup (external drives, use case, comfort level) before diving in
- **Prioritized recommendations**: Grouped into safety tiers — lower-risk caches, movable data, and items requiring judgment
- **Markdown report**: Generates a saved report with ranked findings and manual action suggestions
- **Always asks first**: Never runs cleanup commands or command suggestions without explicit approval

## Typical Space Recovery

On a developer's Mac, this skill typically identifies **50-150 GB** of reclaimable space from:
- Package manager caches (npm, pip, yarn, Homebrew, Cargo)
- Time Machine local snapshots, which are invisible to Finder
- App update staging caches, especially Electron apps like VS Code, Claude, Slack, Cursor, and similar tools
- Build artifacts such as Rust `target/` folders and dormant `node_modules`
- Cloud sync metadata from Google Drive, iCloud, Dropbox, or similar tools

## Quickstart

Install the local wrapper:

```bash
bash install.sh
```

If the installer says `~/.local/bin` is not on your PATH, add it:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Check your setup:

```bash
freeup-space doctor
```

Run the default read-only workflow:

```bash
freeup-space
```

The default workflow saves:

```text
~/Desktop/FreeUp-Space-Audit.txt
~/Desktop/FreeUp-Space-Report.md
```

If either file already exists, FreeUp Space uses timestamped names instead of overwriting it.

For a controlled run that does not open the report automatically:

```bash
freeup-space \
  --audit-output /tmp/freeup-space-audit.txt \
  --report-output /tmp/freeup-space-report.md \
  --no-open \
  --non-interactive
```

Run explicit audit and report commands:

```bash
freeup-space audit --output /tmp/freeup-space-audit.txt
freeup-space report --input /tmp/freeup-space-audit.txt --output ~/Desktop/FreeUp-Space-Report.md
```

Generate a text-only plan from an audit file:

```bash
freeup-space plan --input /tmp/freeup-space-audit.txt
```

The plan prints findings and manual action suggestions. It does not execute
the suggested commands.

Developer and model-review modes use the same safe v0.2 audit/report path and print mode context:

```bash
freeup-space dev
freeup-space models
```

Uninstall only the wrapper:

```bash
bash uninstall.sh
```

Live disk audits require macOS. The report generator, doctor command, and fixture-based tests can run on Linux CI, but live audit data depends on macOS tools such as `diskutil`, `tmutil`, `du`, and `open`.

Command suggestions in reports are recommendations only. FreeUp Space v0.2 does not execute them.
Review the generated report before running any command yourself.
Inspect the top findings, audit coverage, lower-risk cache table, and command
suggestion section before deciding what to do next.

## Mac Tools Federation

This checkout also contains a local file-based federation contract for FreeUp
Space and mac-app-audit. See `FEDERATION.md` for the boundary:

- FreeUp Space owns disk-space and reclaimable-storage findings.
- mac-app-audit owns app, Homebrew package, tool-choice, and alternatives findings.
- Cross-product seams use ledger `related_entries`, not shared runtime code.
- No umbrella CLI, daemon, telemetry, cleanup execution, or app uninstall execution is part of v0.1.

Federation validation:

```bash
cd MAC_App_Audit
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 test_validator.py
cd ..
python3 tests/test_federation_contract.py
```

## Use With Codex

This repository is now structured so Codex can understand, test, and safely modify it.

Start with:

```bash
cat AGENTS.md
cat GOAL.md
```

Then ask Codex to work from one of the task packs in `codex/tasks.md`, for example:

```text
Read AGENTS.md, GOAL.md, and codex/tasks.md. Implement Task Pack 1 only. Do not add cleanup execution. Preserve the no-delete-without-approval safety contract. Run the validation commands before summarizing changes.
```

Recommended validation commands:

```bash
bash -n scripts/disk_audit.sh
bash -n install.sh
bash -n uninstall.sh
python3 -m py_compile scripts/generate_report.py
python3 -m py_compile scripts/freeup_space.py
python3 tests/smoke_test.py
python3 tests/test_cli_smoke.py
python3 tests/test_public_readiness.py
python3 tests/test_federation_contract.py
```

## Installation

### One-Command CLI

Use the repo-local installer:

```bash
bash install.sh
freeup-space doctor
freeup-space
```

The installer writes one wrapper at `~/.local/bin/freeup-space`. It does not use `sudo`, run an audit, or clean anything.

### As a Claude Skill

Download `disk-cleanup.skill` from [Releases](../../releases) and install it in Claude Desktop / Cowork, or copy the skill folder into your Claude skills directory.

### Manual Use

You can also run the scripts directly:

```bash
python3 scripts/freeup_space.py --help
python3 scripts/freeup_space.py doctor
python3 scripts/freeup_space.py --audit-output /tmp/freeup-space-audit.txt --report-output /tmp/freeup-space-report.md --no-open --non-interactive
python3 scripts/freeup_space.py report --input tests/fixtures/sample_audit.txt --output /tmp/freeup-space-report.md
bash scripts/disk_audit.sh /tmp/audit.txt
python3 scripts/generate_report.py /tmp/audit.txt ~/Desktop/disk-report.md
```

The audit script is read-only. It reports disk usage; it does not delete, move, thin snapshots, clear caches, or run `sudo`.

## File Structure

```text
├── AGENTS.md                          # Codex operating instructions and safety contract
├── FEDERATION.md                      # File-based federation contract for FreeUp and mac-app-audit
├── GOAL.md                            # Build goal and handoff brief
├── SKILL.md                           # Claude skill instructions
├── install.sh                         # No-sudo installer for ~/.local/bin/freeup-space
├── uninstall.sh                       # Removes only the installed wrapper
├── MAC_App_Audit/                     # Flat federation contract bundle and planned app-audit goal
├── codex/
│   └── tasks.md                       # Codex task packs / implementation backlog
├── scripts/
│   ├── disk_audit.sh                  # Standalone macOS disk audit script
│   ├── freeup_space.py                # User-facing CLI wrapper
│   └── generate_report.py             # Converts audit data to markdown report
├── references/
│   └── safe-cleanup-targets.md        # Comprehensive reference of safe cleanup targets
├── tests/
│   ├── smoke_test.py                  # Cross-platform report-generation smoke test
│   ├── test_cli_smoke.py              # Fixture-based CLI and installer smoke test
│   ├── test_federation_contract.py    # Fixture-based federation contract smoke test
│   ├── test_public_readiness.py       # Public-readiness copy and workflow regression test
│   └── fixtures/sample_audit.txt      # Synthetic macOS audit fixture
└── evals/
    └── evals.json                     # Skill evaluation cases
```

## Requirements

- macOS for live disk audits; the audit uses `diskutil`, `tmutil`, `du`, and other macOS-specific tools
- Bash and Python 3 for standalone scripts and the `freeup-space` wrapper
- Optional: Claude Desktop/Cowork or Codex for agentic use

## Safety Model

This project separates **audit**, **recommendation**, and **cleanup execution**.

1. The audit script is read-only.
2. The report generator creates recommendations and manual action suggestions but does not execute them.
3. Command suggestions must be shown to the user and explicitly approved before execution.
4. User data should be moved rather than deleted when there is uncertainty.
5. Destructive commands must never be hidden inside tests, automation, or convenience scripts.

## License

MIT
