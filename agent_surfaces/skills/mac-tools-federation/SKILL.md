---
name: mac-tools-federation
description: Use when the user asks how FreeUp Space and MAC_App_Audit work together, asks for federation validation, asks which tool owns a finding, or wants Codex/Claude Code to route between storage cleanup and app/tool-choice audit workflows.
---

# Mac Tools Federation

Use this skill to route work between FreeUp Space and mac-app-audit.
The federation is a file contract, not an umbrella runtime.

## Source Files

Read as needed:

- `FEDERATION.md`
- `GOAL.md`
- `GOAL_AGENT_NATIVE_READINESS.md`
- `MAC_App_Audit/README.md`
- `MAC_App_Audit/SAFETY_CONTRACT.md`
- `MAC_App_Audit/CONVENTIONS.md`
- `MAC_App_Audit/ledger-entry.schema.json`
- `MAC_App_Audit/example_ledger.json`
- `MAC_App_Audit/HANDOFF_v0.1.md`
- `agent_surfaces/skills/freeup-space/SKILL.md`
- `agent_surfaces/skills/mac-app-audit/SKILL.md`

## Routing Rules

- FreeUp Space owns disk-space findings: caches, rebuildable artifacts, large
  files, local model bytes, and reclaimable storage recommendations.
- mac-app-audit owns software-choice findings: apps, Homebrew formulae/casks,
  redundant tools, superseded tools, keep decisions, and alternatives review.
- Local AI model bytes belong to FreeUp Space; local AI runners belong to
  mac-app-audit.
- Homebrew cache cleanup belongs to FreeUp Space; Homebrew package keep/remove
  recommendations belong to mac-app-audit.
- Cross-product references use ledger `related_entries`.
- Do not build an umbrella CLI, daemon, background service, telemetry channel,
  cleanup executor, app uninstall executor, or shared mutable runtime.

## Validation

Run from the source repo root:

```bash
cd MAC_App_Audit
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 test_validator.py
cd ..
python3 tests/test_federation_contract.py
```

Then inspect the example ledger and confirm both `freeup-space` and
`mac-app-audit` producers exist with at least one cross-producer
`related_entries` seam.
