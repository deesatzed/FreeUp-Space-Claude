# mac-tools-federation

This is not a product. It's the paper agreement that lets independent Mac
tools — `mac-app-audit`, `FreeUp Space`, and whatever comes after them —
share a decision-ledger format and a safety posture without sharing a
codebase, a release cycle, or a language.

Federation-by-files: three small contracts, no runtime, no service, no
shared library beyond an optional validator.

## What's here

Current local checkout note: this bundle is flat under `MAC_App_Audit/`.
Canonical federation paths may use `schema/`, `validator/`, `examples/`, and
`tests/`, but this checked-in bundle currently validates with the flat paths
shown below.

Agent-surface note: the parent repo now includes a manager skill and command
for this bundle under `agent_surfaces/skills/mac-app-audit/SKILL.md` and
`agent_surfaces/commands/audit-apps.md`. Those surfaces are truthful routers;
they do not claim the missing collector/writer pipeline exists yet.

| File | Purpose |
|---|---|
| `ledger-entry.schema.json` | The versioned JSON Schema every ledger entry must satisfy. |
| `CHANGELOG.md` | Schema version history and the compatibility rules. |
| `SAFETY_CONTRACT.md` | Non-negotiable automation/safety rules, shared verbatim across products. |
| `CONVENTIONS.md` | File locations, naming, timestamp format — the boring stuff that has to match. |
| `validate_ledger.py` | Standalone validator. Any product (or CI) can run it against its ledger file. |
| `example_ledger.json` | A realistic ledger with entries from two different producers, including a cross-referenced pair. |
| `test_validator.py` | Proves the validator accepts the good example and rejects a broken one. |
| `HANDOFF_2026-07-03.md` | Current handoff documenting the flat layout and implementation-root mismatch. |

## How a product adopts the federation

1. Vendor or reference `SAFETY_CONTRACT.md` unmodified — no product gets to
   loosen it.
2. Write its own ledger file at the path defined in `CONVENTIONS.md`, with
   every entry validating against the current schema.
3. Set `producer` and `producer_version` on every entry it writes. Never
   edit another producer's entries — only read them.
4. Ignore unknown fields on read. The schema is additive-only within a
   major version specifically so producers don't need to coordinate
   releases to stay compatible.
5. Optionally, cross-reference: a report can read a sibling product's
   ledger and cite specific `entry_id`s at seam points (e.g. mac-app-audit
   citing a FreeUp Space model-storage finding). This is a file read, not
   an integration.

## What deliberately is NOT here

- No shared Python/JS library. A product can be bash, Python, or anything
  else — the contract is the JSON on disk, not a function signature.
- No umbrella CLI, dispatcher, or "suite" packaging. That's a legitimate
  future idea, but the rule this repo enforces is: **two independent,
  working ledger producers must exist before any abstraction gets
  extracted above them.** Right now there's headroom for one (mac-app-audit)
  and a planned second (FreeUp Space, once it reaches its own v0.6 cleanup
  plan engine) — that's not yet two, so no umbrella gets built yet.
- No telemetry, no network calls, no daemon. This repo is three documents,
  a schema, and a validator script.

## Validate this flat bundle

Run from `MAC_App_Audit/`:

```bash
python3 -m py_compile validate_ledger.py test_validator.py
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 test_validator.py
```

The validator uses the `jsonschema` Python package when it is available. In a
fresh clone without extra packages, it falls back to a standard-library
validator for the bundled schema subset. Tests and helper scripts must not
install packages automatically.

## Versioning philosophy

`schema_version` follows semver. Within a major version, only additive,
optional fields may be introduced — a producer or consumer built against
`1.0.0` must keep working unmodified against `1.3.0`. Breaking changes
(removing/renaming/re-typing a required field) require a major bump and a
migration note in `schema/CHANGELOG.md`. Nobody is required to adopt a new
major version; old ledgers remain valid documents of record even if a
product later moves on.
