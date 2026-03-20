# FreeUp Space - Claude Disk Cleanup Skill

A Claude Code / Cowork skill that performs comprehensive macOS disk analysis, identifies reclaimable space, and provides prioritized cleanup recommendations with safe, user-approved execution.

## What It Does

- **Full disk audit**: APFS volumes, Time Machine snapshots, app caches, dev tool caches, cloud sync overhead
- **Smart questioning**: Asks about your setup (external drives, use case, comfort level) before diving in
- **Prioritized recommendations**: Grouped into safety tiers — safe caches, movable data, and items requiring judgment
- **Markdown report**: Generates a saved report with ranked findings and exact cleanup commands
- **Always asks first**: Never runs cleanup commands without explicit approval

## Typical Space Recovery

On a developer's Mac, this skill typically identifies **50-150 GB** of reclaimable space from:
- Package manager caches (npm, pip, yarn, Homebrew, Cargo)
- Time Machine local snapshots *invisible to Finder)
- App update staging caches (Electron apps like VSCode, Claude, Slack)
- Build artifacts (Rust targets, node_modules in dormant projects)
- Cloud sync metadata (Google Drive, iCloud, Dropbox)

## Installation

### As a Claude Skill
Download `disk-cleanup.skill` from [Releases](../../releases) and install it in Claude Desktop / Cowork, or copy the skill folder into your Claude skills directory.

### Manual Use
You can also run the audit script standalone:
```bash
bash scripts/disk_audit.sh /tmp/audit.txt
python3 scripts/generate_report.py /tmp/audit.txt ~/Desktop/disk-report.md
```

## File Structure

```
├── SKILL.md                          # Main skill instructions (5-phase workflow)
├── scripts/
│   ├── disk_audit.sh                 # Standalone macOS disk audit script
│   └── generate_report.py            # Converts audit data to markdown report
├── references/
│   └── safe-cleanup-targets.md       # Comprehensive reference of safe cleanup targets
└── evals/
    └── evals.json                    # Test cases for skill evaluation
```

## Requirements

- macOS (uses `diskutil`, `tmutil`, `du`, and other macOS-specific tools)
- Claude Desktop with Cowork mode, or Claude Code with `osascript` MCP access
- For standalone scripts: bash, Python 3

## License

MIT
