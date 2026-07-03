# Conventions

The parts that have to match exactly for file-based federation to work,
kept deliberately small.

## Ledger file location

```
~/.local/share/mac-tools-federation/ledgers/<producer>.ledger.json
```

Examples:
```
~/.local/share/mac-tools-federation/ledgers/mac-app-audit.ledger.json
~/.local/share/mac-tools-federation/ledgers/freeup-space.ledger.json
```

Each file is a JSON array of entries conforming to
`ledger-entry.schema.json` in this flat local contract bundle, or
`schema/ledger-entry.schema.json` in a canonical standalone federation
checkout. One file per producer — never write into another producer's file.

Rationale for `~/.local/share` over `~/Desktop` or a repo-local path: it
survives repo re-clones, isn't accidentally synced to cloud storage or
git, and matches XDG-ish convention on a Mac dev machine without requiring
Linux XDG env vars to be set.

## Reading a sibling's ledger

Any product may read (never write) another producer's ledger file to cite
entries at seam points in its own report. This is a plain file read — no
IPC, no socket, no API. If the file doesn't exist, treat the sibling
product as "not installed" and omit seam references silently; don't error.

## Timestamps

ISO 8601, UTC, with `Z` suffix. `2026-07-03T18:45:00Z`. No local-time
timestamps in ledger entries — reports may render local time for display,
but stored values are always UTC.

## entry_id derivation (recommended, not schema-enforced)

`sha256(producer + ":" + subject.identifier)[:16]`, falling back to
`subject.name` if no stable `identifier` exists. Deterministic derivation
means re-running an audit updates an existing entry's `updated_at` rather
than creating a duplicate every run.

## Report file naming (for human-facing outputs, not ledgers)

```
~/Desktop/<Product-Name>-Report-<YYYY-MM-DD-HHMMSS>.md
```

Matches the FreeUp Space handoff's existing convention. Timestamp suffix
only added when a same-day file would otherwise be overwritten; don't
timestamp every single run if it's the first one that day.

## Validator usage

From this flat local bundle:

```bash
python3 validate_ledger.py example_ledger.json --schema ledger-entry.schema.json
python3 test_validator.py
```

Against a live producer ledger from this flat bundle:

```bash
python3 validate_ledger.py ~/.local/share/mac-tools-federation/ledgers/mac-app-audit.ledger.json --schema ledger-entry.schema.json
```

Canonical standalone federation layout, if restored later:

```bash
python3 validator/validate_ledger.py ~/.local/share/mac-tools-federation/ledgers/mac-app-audit.ledger.json
```

Exit code 0 means every entry is valid; non-zero output includes a per-entry
error list or usage/environment error. Any producer's test suite should run
this against its own ledger output as part of CI/smoke testing, the same way
FreeUp's `smoke_test.py` validates report generation today.
