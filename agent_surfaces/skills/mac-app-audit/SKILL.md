---
name: mac-app-audit
description: Use when the user asks Codex or Claude Code to audit Mac apps, Homebrew formulae/casks, redundant tools, superseded tools, app keep/remove decisions, alternatives research, or the MAC_App_Audit federation bundle. This skill is the manager layer; deterministic scripts and slash commands are helpers.
---

# MAC App Audit

Use this skill as the Claude Code/Codex manager for mac-app-audit. The intended
product surface is a skill plus command workflow, not a standalone app.

## Required Preflight

Read these first from the active source checkout:

1. `MAC_App_Audit/HANDOFF_v0.1.md`
2. `MAC_App_Audit/GOAL.md`
3. `MAC_App_Audit/README.md`
4. `MAC_App_Audit/SAFETY_CONTRACT.md`
5. `MAC_App_Audit/CONVENTIONS.md`
6. `FEDERATION.md`

Then identify whether the current directory is:

- the real mac-app-audit implementation root, containing `SKILL.md`,
  `scripts/collect_inventory.sh`, and `commands/audit-apps.md`; or
- the flat federation contract bundle currently observed under
  `MAC_App_Audit/`.

If only the flat bundle is present, do not pretend a complete app-audit
pipeline exists. Validate the bundle, explain the missing implementation root,
and work from `MAC_App_Audit/GOAL.md` before building.

## Operating Model

The intended architecture from `HANDOFF_v0.1.md` is:

- scripts: deterministic collection, usage counts, dependency graph signals,
  ledger read/write, schema validation;
- Claude Code or Codex: classification, redundancy clusters, alternatives
  research, report prose, and user-facing summary;
- ledger + report: durable machine-readable record plus human-readable output.

Do not merge FreeUp Space storage logic into mac-app-audit. Cross-product seams
use federation ledger `related_entries`, not code calls.

## Safety

- Default is audit/report only.
- Recommendation commands may be shown as inert text only.
- Do not uninstall apps, remove Homebrew packages, migrate tools, install
  alternatives, run `sudo`, mutate live ledgers, read raw shell history into a
  prompt, or start daemons.
- Derive local usage counts with deterministic scripts before asking the model
  to interpret them.

## Current Bundle Validation

When working in the current flat bundle, run:

```bash
cd MAC_App_Audit
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 validate_ledger.py example_ledger.json
python3 test_validator.py
cd ..
python3 tests/test_federation_contract.py
```

If asked to implement v0.2 and the implementation root is still absent, first
create or locate the skill/command root required by `MAC_App_Audit/GOAL.md`.
