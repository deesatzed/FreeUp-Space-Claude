---
allowed-tools: Read, Glob, Grep, Bash
argument-hint: [doctor|audit|report|plan|validate] [optional path]
description: Run the FreeUp Space agent-managed storage workflow through Codex or Claude Code. Scripts are read-only helpers; no cleanup is executed.
---

# FreeUp Space Command

Use the `freeup-space` skill instructions. Treat Codex or Claude Code as the
manager and the repo scripts as deterministic helpers.

Parse `$ARGUMENTS`:

- `doctor`: run `python3 scripts/freeup_space.py doctor`.
- `audit`: run the read-only helper with explicit `/tmp` outputs and `--no-open`.
- `report`: generate or inspect a report from the provided audit path.
- `plan`: print advisory findings from the provided audit path.
- `validate`: run the documented validation commands.
- no argument: read `AGENTS.md`, `GOAL_AGENT_NATIVE_READINESS.md`, and
  `README.md`, then recommend the safest next command.

Never execute cleanup, `sudo`, app uninstall, package install, live ledger
writes, telemetry, or daemon setup.
