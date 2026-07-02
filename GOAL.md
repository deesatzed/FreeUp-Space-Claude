# GOAL.md — Codex Handoff for FreeUp Space

## Build Goal

Convert this repository from a Claude-only disk cleanup skill into a **Codex-ready macOS storage analysis toolkit** that can be safely maintained, tested, and extended by coding agents.

The repo should remain small, dependency-light, and safety-first.

## User Need

Mac users often see low-storage warnings but cannot tell whether the problem is visible files, APFS snapshots, developer caches, cloud sync overhead, app caches, large applications, or hidden Library growth.

The tool should help them answer four questions:

1. What is using my disk?
2. What is safe to clear?
3. What should be moved rather than deleted?
4. What exact commands or GUI steps should I approve next?

## Non-Negotiable Safety Requirements

- No automatic deletion.
- No hidden cleanup in tests or helper scripts.
- No `sudo` unless the user explicitly approves a specific command batch.
- No destructive batch action without a before/after check.
- No deletion of user documents, photos, movies, music, cloud sync folders, or project folders.
- Always explain the tradeoff of removing caches: safe, but may require re-download/rebuild.

## Current State

The repository already contains:

- A Claude skill workflow in `SKILL.md`.
- A read-only audit script in `scripts/disk_audit.sh`.
- A Markdown report generator in `scripts/generate_report.py`.
- A reference file of cleanup targets.
- Skill eval cases.

The Codex conversion adds:

- `AGENTS.md` for coding-agent operating rules.
- This `GOAL.md` handoff.
- `codex/tasks.md` for focused task packs.
- CI/smoke testing scaffolding.
- A more robust read-only audit script that does not abort on missing optional paths.

## MVP Definition

Codex should be able to:

1. Read the repository purpose and safety constraints without external context.
2. Run non-destructive validation commands.
3. Modify the audit/report scripts without breaking cross-platform smoke tests.
4. Preserve the user-approval cleanup model.
5. Produce a clearer Markdown report from a synthetic audit fixture.

## Recommended Next Build Sequence

### Phase 1 — Stabilize Existing Scripts

- Keep `disk_audit.sh` read-only.
- Ensure it survives missing optional paths like `/opt/homebrew`, `~/Projects`, `~/.docker`, and cloud sync folders.
- Ensure paths with spaces work.
- Ensure CI can run syntax checks on Linux without live macOS tooling.

### Phase 2 — Improve Report Quality

- Rank all findings by parsed size.
- Add a top-25 findings table.
- Separate recommendations into:
  - Tier 1: safe/regenerable caches
  - Tier 2: move/archive candidates
  - Tier 3: judgment-required removals
- Include exact command snippets but do not execute them.
- Add caution notes for cloud sync and app support data.

### Phase 3 — Structured Audit Output

- Add optional JSON output from `disk_audit.sh`, or create a Python audit collector.
- Preserve the text format for human debugging.
- Update `generate_report.py` to prefer JSON when available.

### Phase 4 — Guided Interactive Mode

- Add a `freeup_space.py` wrapper that asks symptom/setup questions, runs the audit, generates the report, and presents recommended next actions.
- Still require explicit confirmation before any cleanup command.

### Phase 5 — Packaging

- Add a release build for Claude skill packaging if desired.
- Add example reports.
- Add clearer installation instructions for Claude, Codex, and standalone terminal use.

## Acceptance Criteria

- `bash -n scripts/disk_audit.sh` passes.
- `python3 -m py_compile scripts/generate_report.py` passes.
- `python3 tests/smoke_test.py` passes.
- README explains Codex usage.
- `AGENTS.md` clearly prevents destructive automation.
- Any future PR that changes cleanup behavior documents the safety impact.

## Out of Scope for MVP

- A GUI app.
- Automatic cleanup.
- Background daemon behavior.
- Replacing macOS Storage Management.
- Deep full-disk indexing.
- Permanent deletion of user files.
