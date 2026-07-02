# FreeUp Space - Mac Disk Cleanup Skill

A Claude/Codex-friendly macOS disk cleanup assistant that performs comprehensive disk analysis, identifies reclaimable space, and provides prioritized cleanup recommendations with safe, user-approved execution.

## What It Does

- **Full disk audit**: APFS volumes, Time Machine snapshots, app caches, dev tool caches, cloud sync overhead
- **Smart questioning**: Asks about your setup (external drives, use case, comfort level) before diving in
- **Prioritized recommendations**: Grouped into safety tiers — safe caches, movable data, and items requiring judgment
- **Markdown report**: Generates a saved report with ranked findings and exact cleanup commands
- **Always asks first**: Never runs cleanup commands without explicit approval

## Typical Space Recovery

On a developer's Mac, this skill typically identifies **50-150 GB** of reclaimable space from:
- Package manager caches (npm, pip, yarn, Homebrew, Cargo)
- Time Machine local snapshots, which are invisible to Finder
- App update staging caches, especially Electron apps like VS Code, Claude, Slack, Cursor, and similar tools
- Build artifacts such as Rust `target/` folders and dormant `node_modules`
- Cloud sync metadata from Google Drive, iCloud, Dropbox, or similar tools

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
python3 -m py_compile scripts/generate_report.py
python3 tests/smoke_test.py
```

## Installation

### As a Claude Skill

Download `disk-cleanup.skill` from [Releases](../../releases) and install it in Claude Desktop / Cowork, or copy the skill folder into your Claude skills directory.

### Manual Use

You can also run the audit script standalone:

```bash
bash scripts/disk_audit.sh /tmp/audit.txt
python3 scripts/generate_report.py /tmp/audit.txt ~/Desktop/disk-report.md
```

The audit script is read-only. It reports disk usage; it does not delete, move, thin snapshots, clear caches, or run `sudo`.

## File Structure

```text
├── AGENTS.md                          # Codex operating instructions and safety contract
├── GOAL.md                            # Build goal and handoff brief
├── SKILL.md                           # Claude skill instructions
├── codex/
│   └── tasks.md                       # Codex task packs / implementation backlog
├── scripts/
│   ├── disk_audit.sh                  # Standalone macOS disk audit script
│   └── generate_report.py             # Converts audit data to markdown report
├── references/
│   └── safe-cleanup-targets.md        # Comprehensive reference of safe cleanup targets
├── tests/
│   ├── smoke_test.py                  # Cross-platform report-generation smoke test
│   └── fixtures/sample_audit.txt      # Synthetic macOS audit fixture
└── evals/
    └── evals.json                     # Skill evaluation cases
```

## Requirements

- macOS for live disk audits; the audit uses `diskutil`, `tmutil`, `du`, and other macOS-specific tools
- Bash and Python 3 for standalone scripts
- Optional: Claude Desktop/Cowork or Codex for agentic use

## Safety Model

This project separates **audit**, **recommendation**, and **cleanup execution**.

1. The audit script is read-only.
2. The report generator creates recommendations but does not execute them.
3. Cleanup commands must be shown to the user and explicitly approved before execution.
4. User data should be moved rather than deleted when there is uncertainty.
5. Destructive commands must never be hidden inside tests, automation, or convenience scripts.

## License

MIT
