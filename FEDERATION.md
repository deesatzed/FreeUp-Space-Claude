# Mac Tools Federation

This repository currently contains two local Mac-tool surfaces:

- `/Users/o2satz/FreeUp-Space-Claude`
- `/Users/o2satz/FreeUp-Space-Claude/MAC_App_Audit`

The federation is the file contract between them. It is not an app, daemon,
server, umbrella CLI, package manager, installer, or cleanup executor.

## Producers

| Producer | Current path | Owns | Current status |
|---|---|---|---|
| `freeup-space` | `/Users/o2satz/FreeUp-Space-Claude` | Disk-space findings, cache bloat, rebuildable artifacts, large files, model bytes, and reclaimable storage recommendations | Codex/Claude skill and command surfaces plus working v0.2 helper CLI/report path; no default live ledger writer in this federation goal |
| `mac-app-audit` | `/Users/o2satz/FreeUp-Space-Claude/MAC_App_Audit` | App/tool-choice findings, Homebrew package keep/remove recommendations, redundant tools, superseded tools, keep decisions, and alternatives review | Current directory is a flat federation contract bundle plus an installable manager skill/command; full skill/command implementation root still must be located or created before app-audit v0.2 work starts |

## Boundary

FreeUp Space and mac-app-audit stay independent. They may share ledger
language and safety rules, but they must not call each other's code or share
mutable runtime state.

Overlap ownership:

- Homebrew cache cleanup belongs to `freeup-space`.
- Homebrew formula/cask keep, remove, redundant, or superseded findings belong
  to `mac-app-audit`.
- Local AI model bytes and duplicate quantizations belong to `freeup-space`.
- Local AI runners and app/tool choice belong to `mac-app-audit`.
- Unknown or mixed findings should be linked by ledger entries, not solved by
  merging product logic.

## Ledger Contract

Each producer writes only its own ledger:

```text
~/.local/share/mac-tools-federation/ledgers/freeup-space.ledger.json
~/.local/share/mac-tools-federation/ledgers/mac-app-audit.ledger.json
```

Rules:

1. One producer may read another producer's ledger.
2. A producer must never write another producer's ledger.
3. Missing sibling ledgers are not errors.
4. Cross-product seams use `related_entries` and stable `entry_id` values.
5. Consumers ignore unknown fields so the schema can evolve additively.
6. Ledger writes are records and recommendations, not cleanup actions.

The bundled example ledger in `MAC_App_Audit/example_ledger.json` includes both
`mac-app-audit` and `freeup-space` entries. It also contains a cross-producer
`related_entries` seam between a FreeUp model-storage finding and a
mac-app-audit runner assessment.

## Local Contract Bundle

`MAC_App_Audit/` is currently a flat local federation contract bundle:

```text
MAC_App_Audit/CHANGELOG.md
MAC_App_Audit/CONVENTIONS.md
MAC_App_Audit/GOAL.md
MAC_App_Audit/HANDOFF_2026-07-03.md
MAC_App_Audit/HANDOFF_LATEST.md
MAC_App_Audit/HANDOFF_v0.1.md
MAC_App_Audit/README.md
MAC_App_Audit/SAFETY_CONTRACT.md
MAC_App_Audit/example_ledger.json
MAC_App_Audit/ledger-entry.schema.json
MAC_App_Audit/test_validator.py
MAC_App_Audit/validate_ledger.py
```

Validate it from the repository root:

```bash
cd MAC_App_Audit
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 test_validator.py
```

Root federation smoke:

```bash
python3 tests/test_federation_contract.py
```

Agent-native surfaces:

```bash
bash scripts/install_agent_surfaces.sh
python3 tests/test_agent_surfaces.py
```

## Safety Floor

The federation inherits the stricter of the product-local safety contract and
`MAC_App_Audit/SAFETY_CONTRACT.md`.

Non-negotiables:

1. No automatic deletion, cache clearing, snapshot thinning, app uninstall, or
   package install by default.
2. No hidden cleanup in wrappers, helpers, tests, or validators.
3. No `sudo` unless a future explicitly approved execution mode shows the
   exact command batch and receives typed confirmation.
4. No telemetry, daemon, launch agent, background collector, or network service.
5. Recommendations without evidence must be marked as unverified or
   `not_assessed`.
6. When unsure, preserve, move, archive, or investigate instead of deleting.

## Not In v0.1

This federation completion does not build:

- an umbrella `freeup` command,
- a shared Python library,
- a daemon or service,
- a Homebrew tap,
- cleanup execution,
- app uninstall execution,
- live ledger writing for FreeUp Space,
- the full mac-app-audit collector/writer/delta-mode implementation.

Those may only be considered after both independent producers have their own
verified ledger-producing paths.
