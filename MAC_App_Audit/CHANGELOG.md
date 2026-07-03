# Schema Changelog

Format follows semver. See `README.md` for the compatibility promise this
enforces.

## 1.0.0 — 2026-07-03

Initial schema. Defines:
- Core envelope: `schema_version`, `entry_id`, `producer`, `producer_version`,
  `created_at` / `updated_at`.
- `subject` — what the entry is about (app, homebrew formula/cask, path,
  model, cache, other).
- `verdict` — closed enum: `keep`, `redundant`, `superseded`, `reclaimable`,
  `investigate`, `judgment_required`, `do_not_touch`, `not_assessed`.
- `confidence_basis` — forces every verdict to declare its method
  (`usage_telemetry`, `dependency_graph`, `web_search_citation`,
  `filesystem_stat`, `manual`, `heuristic`); numeric confidence only
  permitted alongside a data-backed method, never alongside `manual`/
  `heuristic`.
- `evidence[]` — receipts array; citations must carry `source_url` and
  `fetched_at` where `type` is `citation`.
- `decision` — user's accept/reject/defer state, with `reason` explicitly
  supported to capture revealed preference on rejection.
- `related_entries` — cross-referencing, used both for within-producer
  clusters (e.g. a redundancy group) and cross-product seam links.

## Compatibility rules (apply to every future entry)

1. **Additive only within a major version.** New optional fields may be
   added freely. Existing required fields may never be removed, renamed, or
   have their type narrowed without a major bump.
2. **Consumers must ignore unknown fields.** `additionalProperties: true`
   is intentional at every level — a consumer built against 1.0.0 must not
   error when reading an entry written by a 1.4.0 producer with extra
   fields.
3. **Enums grow, they don't shrink.** Adding a new `verdict` or
   `confidence_basis.method` value is a minor bump. Removing one, or
   changing what an existing value means, is a major bump.
4. **`entry_id` stability is a producer responsibility**, not something
   this schema can enforce structurally — but producers should derive it
   deterministically (e.g. hash of `producer` + `subject.identifier`) so
   re-running an audit updates an entry via `updated_at` rather than
   creating a duplicate.
5. **Old ledgers remain valid documents of record.** A major version bump
   does not obligate anyone to migrate historical entries; it only governs
   what new entries must look like.

## Planned, not yet scheduled

- `2.0.0` candidate idea (not committed): a `superseded_by` field pointing
  directly at a replacement `entry_id` when `verdict: superseded`, rather
  than relying on prose in `notes`. Deferred until a second real producer's
  usage shows whether this is actually needed or over-engineering.
