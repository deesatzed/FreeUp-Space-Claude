# GOAL_AGENT_NATIVE_READINESS.md - Codex/Claude Native Readiness Contract

Use this file from the repository root with:

```text
/goal GOAL_AGENT_NATIVE_READINESS.md
```

## OUTCOME

Make FreeUp Space, MAC_App_Audit, and their federation usable as Codex/Claude
native skill and command surfaces.

This is not a standalone-app readiness goal. The product boundary is:

- Codex or Claude Code is the manager.
- Skills and command markdown are the primary invocation surfaces.
- Bash/Python scripts are deterministic read-only helpers.
- The federation is a file contract: schema, ledger conventions, safety rules,
  validator, and cross-product `related_entries`.

## CURRENT TRUTH

1. FreeUp Space has a repo-local `SKILL.md` and deterministic helper scripts.
2. `MAC_App_Audit/` is currently a flat federation contract bundle, not the
   complete skill/command implementation root described by
   `MAC_App_Audit/HANDOFF_v0.1.md`.
3. The missing MAC_App_Audit implementation files are still:
   `SKILL.md`, `scripts/collect_inventory.sh`, `commands/audit-apps.md`, and
   fixture data for the full app-audit pipeline.
4. This repo now includes installable agent surfaces under `agent_surfaces/`:
   - `agent_surfaces/skills/freeup-space/SKILL.md`
   - `agent_surfaces/skills/mac-app-audit/SKILL.md`
   - `agent_surfaces/skills/mac-tools-federation/SKILL.md`
   - `agent_surfaces/commands/freeup-space.md`
   - `agent_surfaces/commands/audit-apps.md`
   - `agent_surfaces/commands/mac-tools-federation.md`

## PROOF OF DONE

Run from the repository root:

```bash
pwd
git status --short --branch
git remote -v
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
cd MAC_App_Audit
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 test_validator.py
cd ..
```

Install the agent surfaces:

```bash
bash scripts/install_agent_surfaces.sh
```

Confirm installed files exist:

```bash
test -f "$HOME/.codex/skills/freeup-space/SKILL.md"
test -f "$HOME/.codex/skills/mac-app-audit/SKILL.md"
test -f "$HOME/.codex/skills/mac-tools-federation/SKILL.md"
test -f "$HOME/.agents/skills/freeup-space/SKILL.md"
test -f "$HOME/.claude/skills/freeup-space/SKILL.md"
test -f "$HOME/.claude/commands/mac-tools/freeup-space.md"
test -f "$HOME/.claude/commands/mac-tools/audit-apps.md"
test -f "$HOME/.claude/commands/mac-tools/mac-tools-federation.md"
test -f "$HOME/.codex/prompts/mac-tools/freeup-space.md"
test -f "$HOME/.codex/prompts/mac-tools/audit-apps.md"
test -f "$HOME/.codex/prompts/mac-tools/mac-tools-federation.md"
```

Then start a new Codex or Claude Code session, or reload the client, so newly
installed skills and commands are discovered by the agent runtime.

Optional live macOS proof for FreeUp Space:

```bash
python3 scripts/freeup_space.py \
  --audit-output /tmp/freeup-agent-native-audit.txt \
  --report-output /tmp/freeup-agent-native-report.md \
  --no-open \
  --non-interactive
test -s /tmp/freeup-agent-native-audit.txt
test -s /tmp/freeup-agent-native-report.md
```

## SCOPE

Allowed:

- Add or update skill and command markdown.
- Add installer support for Codex/Claude skill and command locations.
- Reframe documentation so the helper CLI is not presented as the primary
  product identity.
- Keep fixture tests and live read-only audit/report proof.

Do not:

- Implement cleanup execution.
- Build an umbrella runtime or shared dispatcher.
- Pretend the flat `MAC_App_Audit/` bundle is the completed app-audit
  skill/command implementation root.
- Install packages, uninstall apps, run `sudo`, start daemons, add telemetry,
  or mutate live ledgers.

## COMPLETE

Mark complete only when:

1. Agent surfaces install into Codex and Claude locations.
2. Docs say Codex/Claude skills and commands are the primary invocation surface.
3. The CLI is described as a deterministic helper/test harness.
4. `MAC_App_Audit` is represented truthfully as a manager skill plus current
   flat federation bundle until the collector pipeline is created or found.
5. All proof commands pass.
