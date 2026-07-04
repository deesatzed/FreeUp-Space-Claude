---
allowed-tools: Read, Glob, Grep, Bash
argument-hint: [preflight|validate-bundle|build-v0.2|delta]
description: Route MAC_App_Audit work through Claude Code or Codex. Validates the federation bundle and refuses to fake the missing collector/skill implementation root.
---

# MAC App Audit Command

Use the `mac-app-audit` skill instructions.

Parse `$ARGUMENTS`:

- `preflight`: inspect whether the active checkout has the real implementation
  root with `SKILL.md`, `scripts/collect_inventory.sh`, and
  `commands/audit-apps.md`.
- `validate-bundle`: validate the current flat federation bundle.
- `build-v0.2`: follow `MAC_App_Audit/GOAL.md`; stop if the implementation
  root is absent unless the user explicitly asks to create it here.
- `delta`: only valid after v0.2 exists; otherwise report that delta mode is
  not implemented.

Never uninstall apps, remove packages, install alternatives, run `sudo`, write
live ledgers, or send raw shell history to a model prompt.
