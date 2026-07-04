---
name: freeup-space
description: Use when the user asks Codex or Claude Code to inspect macOS disk usage, find reclaimable space, generate a FreeUp Space report or plan, package/install the FreeUp skill, or validate the FreeUp storage workflow. This is an agent-managed skill surface: scripts are deterministic helpers, not the product identity.
---

# FreeUp Space

Use this skill as the manager layer for FreeUp Space. The user-facing product is
Claude Code or Codex using this skill plus deterministic read-only scripts.
Do not present FreeUp Space as a standalone cleanup app.

## Source Of Truth

From the repo root, read these before action when present:

1. `AGENTS.md`
2. `GOAL.md`
3. `GOAL_AGENT_NATIVE_READINESS.md`
4. `FEDERATION.md`
5. `README.md`
6. `SKILL.md`

If running from an installed copy of this skill, locate the source checkout
with `FREEUP_SPACE_REPO` or by checking:

- `/Volumes/WS4TB/_tstzone/FreeUp-Space-Claude`
- `/Users/o2satz/FreeUp-Space-Claude`

Stop if no source checkout can be found.

## Operating Model

- Codex or Claude Code is the manager: asks questions, interprets findings,
  writes the report narrative, and keeps safety boundaries visible.
- `scripts/disk_audit.sh`, `scripts/generate_report.py`, and
  `scripts/freeup_space.py` are deterministic helper scripts.
- The helper CLI may be used for verification and repeatability, but the
  intended invocation surface is the skill/command inside Codex or Claude Code.
- Never delete, move, clear caches, thin snapshots, uninstall apps, install
  packages, run `sudo`, write live federation ledgers, or start background
  services unless a future explicit execution goal adds a separate approval
  protocol.

## Standard Workflow

1. Read the source-of-truth files.
2. Confirm the user's storage goal and risk tolerance unless already clear.
3. Run `python3 scripts/freeup_space.py doctor`.
4. For live macOS proof, run the default helper flow with explicit outputs:

   ```bash
   python3 scripts/freeup_space.py \
     --audit-output /tmp/freeup-space-audit.txt \
     --report-output /tmp/freeup-space-report.md \
     --no-open \
     --non-interactive
   ```

5. Inspect the report and summarize:
   - top storage findings,
   - lower-risk caches,
   - judgment-required user/app data,
   - command suggestions clearly marked as not executed.
6. If the user asks for federation context, read `FEDERATION.md` and the
   `MAC_App_Audit/` contract files.

## Validation

Run from the repo root after changes:

```bash
bash -n scripts/disk_audit.sh
bash -n install.sh
bash -n uninstall.sh
bash -n scripts/install_agent_surfaces.sh
python3 -m py_compile scripts/generate_report.py scripts/freeup_space.py
python3 tests/smoke_test.py
python3 tests/test_cli_smoke.py
python3 tests/test_public_readiness.py
python3 tests/test_agent_surfaces.py
python3 tests/test_federation_contract.py
```
