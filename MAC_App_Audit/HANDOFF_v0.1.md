# HANDOFF_v0.1 — mac-app-audit Build Plan

## Purpose of This Handoff

This document is meant to be placed in the root of the local `mac-app-audit`
repository and read by Claude Code or Codex before making changes.

It captures every design decision made during planning so that no context
is lost between sessions or between agents — this repo may be worked on by
Claude Code in one session and Codex in the next, and both must arrive at
the same understanding from this file alone, without re-deriving decisions
already made.

The goal is to convert the current repo from a working skill prototype
(collector script + SKILL.md + slash command) into a ledger-native,
periodically-run Mac software audit tool that gets smarter over time
without becoming reckless, noisy, or bloated.

---

## Relationship to the Federation and to FreeUp Space

`mac-app-audit` is one of (eventually) several independent Mac tools that
share a common contract, defined in the sibling repo `mac-tools-federation`.
**Read that repo's three documents first, in this order, before touching
anything here:**

1. `mac-tools-federation/SAFETY_CONTRACT.md` — non-negotiable automation
   levels and safety rules. This repo inherits it unmodified.
2. `mac-tools-federation/CONVENTIONS.md` — ledger file location, timestamp
   format, `entry_id` derivation.
3. `mac-tools-federation/schema/ledger-entry.schema.json` (+ `CHANGELOG.md`)
   — the schema every ledger entry this tool writes must validate against.

**Ownership boundary vs. FreeUp Space** (a sibling storage-audit tool, built
separately, do not merge or fork logic between the two):

- `mac-app-audit` owns **software choices** — which apps/CLI tools/casks/
  formulae to keep, which are redundant with each other, which have been
  superseded by something better.
- FreeUp Space owns **disk space** — cache bloat, rebuildable artifacts,
  large files, model file storage.
- At the two collision points, the boundary is explicit: for local AI
  models, FreeUp Space owns *the bytes on disk* (duplicate quantizations,
  stale downloads); `mac-app-audit` owns *the runners* (which of Ollama /
  LM Studio / Open WebUI / jan.ai / osaurus / oMLX to actually keep
  installed). For Homebrew, FreeUp Space owns *cache cleanup*
  (`brew cleanup` territory); `mac-app-audit` owns *the packages
  themselves*.
- Cross-references happen only through the shared ledger's
  `related_entries` field (see the federation repo's example ledger for a
  worked example of exactly this seam). Never call into FreeUp Space's
  code or vice versa.
- **Do not build an umbrella/dispatcher command yet.** The federation
  README's explicit rule: two independent, working ledger producers must
  exist before any abstraction gets extracted above them. FreeUp Space
  doesn't write ledger entries until its own v0.6 — until then there is
  only one producer, so no umbrella work belongs in either repo.

---

## Current Repo State

The repo already contains (built in a prior session, do not discard):

- `SKILL.md` — Claude Code skill instructions for classification, scoring,
  the redundancy-cluster pass, and report output format. This is the
  analysis logic and remains largely correct; it needs to be extended
  (see Scope below) to write ledger entries instead of only prose, and to
  incorporate the deterministic-scoring and alternatives-engine additions
  below.
- `scripts/collect_inventory.sh` — read-only macOS data collector. Pulls
  Homebrew formula/cask descriptions via batched `brew info --json=v2`,
  and per-`.app` metadata via `mdls` (last-used date, use count, date
  added, size). **This script does NOT yet parse shell history** — that's
  new scope, see below.
- `commands/audit-apps.md` — slash command wrapper for Claude Code/Codex.
- `README.md` — install instructions for both Claude Code (`~/.claude/`)
  and Codex (`~/.codex/prompts/`).

Recent planning established (do not re-litigate these, they are decided):

1. The scoring model must have a **deterministic backbone the LLM
   interprets, not invents** — usage signals (recency, use count,
   dependency-leaf status, and critically shell-history invocation counts
   for CLI tools, which `mdls` cannot see) computed by the collector script
   as plain numbers, with the agent doing categorization and prose on top,
   not generating confidence percentages from vibes.
2. A **four-verdict taxonomy**, not a single removal score: `keep`
   (affirmative, dated reassurance — this has real value, not just
   silence), `redundant`/`superseded` (grey vs. clear-cut, evidence-gated),
   `investigate` (unclear purpose, tell the user exactly what to check),
   `do_not_touch` (system/dependency component, no percentage needed).
   These map directly onto the federation schema's `verdict` enum.
3. **The alternatives ("better option exists") engine is real and valued**,
   but must be strictly evidence-grounded: usage-proportional (deep-scan
   only the top-N most-used tools; the dormant tail's answer is removal,
   not replacement, and is out of scope for the alternatives engine), live
   search with a recency requirement (a recommendation without a citation
   dated within a bounded window renders as unverified), and fit-checked
   against the user's known stack (Apple Silicon/MLX, Python/SQL/React,
   local-inference-heavy — maintained as an explicit `user_stack_profile`,
   not left implicit in the agent's training-data assumptions). Every
   verdict of `superseded` must also state migration cost, not just
   benefit — a recommendation that only lists upside is marketing, not
   advice.
4. **Anti-churn is a first-class feature.** The tool is rewarded for
   producing `keep` and grey-zone verdicts, not just for finding
   replacements every run. A run that recommends nothing new is a
   successful run, not a failure to find something.
5. **Three-loop cadence**, not one giant periodic run:
   - *Daily*: no agent run at all. Purely passive — see "shell history:
     retroactive reads, not telemetry" below.
   - *Weekly*: a short delta briefing (`--delta` mode) — new installs
     since last run, any ledger entry whose `revisit_after` date arrived,
     and 5 tools rotated into deep alternatives-research (see rotation
     queue below). Meant to be readable in under two minutes.
   - *Monthly/quarterly*: full audit + redundancy cluster pass + report.
     Alternatives research for the top-20 most-used tools is spread across
     the weekly rotation (5/week × 4 weeks) specifically so no single run
     is slow, and so the "SOTA check" picture is always fresh rather than
     stale between quarterly runs.
6. **Rotation queue mechanics**: each tool that clears the usage threshold
   for alternatives-scanning gets a `last_verified` date tracked in its
   ledger entry. The weekly run picks the 5 most-stale-verified tools
   (oldest `last_verified`, or never-verified) rather than a fixed list,
   so the queue self-balances even as the top-20-by-usage set shifts over
   time.
7. **Shell history: retroactive reads, not a background daemon.**
   Explicitly decided against a launchd telemetry collector. Every run —
   daily-equivalent data, weekly, or quarterly — parses `~/.zsh_history`
   (or `~/.bash_history`) retroactively for the relevant lookback window.
   Nothing runs unattended between invocations. This is a firm decision,
   not still open.
8. **Rejected-with-reason is durable signal.** When a user rejects a
   `redundant`/`superseded` verdict via the ledger's `decision.reason`
   field, that reason must be read on subsequent runs and must suppress
   re-suggesting the same class of change, not just the identical entry.
   (Worked example already in the federation repo's example ledger: `rar.app`
   rejected with reason "occasional RAR files from clients," which should
   suppress future archive-tool-consolidation suggestions touching that
   specific app, not the whole cluster.)
9. **Redundancy clustering is a distinct pass**, run after individual
   classification, not folded into per-app scoring. Present clusters
   (e.g. commander-one vs. marta; the six-deep local-inference-runner
   pile; multiple markdown editors) as a group with one recommendation,
   not as independently-scored siblings that happen to overlap.
10. **Guardrails already specified, keep exactly as designed:** hard
    denylist (Apple-signed, running process, referenced in
    LaunchAgents/Daemons, dependency-graph target) is categorical, not a
    low-confidence score; wrapper/helper/updater apps (`*Helper.app`,
    `*Updater.app`, `com.*.notification-agent`) get grouped under their
    parent rather than scored independently; the alternatives engine
    **recommends, never installs or migrates**, full stop, at every
    automation level.

---

## Product North Star

> A periodic Mac software audit assistant for developers and AI-tool power
> users that tells you what you have, why it's there, whether it's still
> earning its place, and — grounded in your actual usage and current
> search results, not guesswork — whether something better now exists for
> the tools you actually rely on.

It should not become:

> A generic app-cleaner that deletes things, or an opinion generator that
> recommends switching tools it has no evidence for.

---

## Primary User

Currently single-user-designed (the repo owner: 20 years of AI/ML
production development, Mac Mini M4 / 64GB unified memory, MLX + Unsloth +
Gemma/Qwen local-inference stack, Python/SQL/React). The
`user_stack_profile` (see Scope below) should be initialized from this
context rather than left generic — a stack-fit check that doesn't know the
user runs MLX-native tooling on Apple Silicon can't actually judge fit.
Keep the profile in a config file, not hardcoded in the skill logic, so it
remains accurate as the stack changes.

---

## Core Design Principle

Same split as FreeUp Space, and intentionally consistent with it per the
federation conventions:

```text
scripts/ (bash/python) = deterministic engine: collection, usage-stat
                          computation, dependency-graph resolution,
                          ledger read/write, schema validation
Claude Code / Codex     = manager: classification, redundancy-cluster
                          reasoning, alternatives research (live search),
                          report prose, user-facing summary
Ledger + Report         = the two decision surfaces — ledger is the
                          durable machine-readable record, report is the
                          human-readable summary generated from it
```

The deterministic engine must be able to produce raw inventory + usage
numbers with no agent involved at all (`collect_inventory.sh` already does
most of this). The agent is required for classification, clustering,
search-grounded alternatives, and prose — never for arithmetic that a
script can do more reliably.

---

## Automation Levels

Inherited from `mac-tools-federation/SAFETY_CONTRACT.md` without
modification. For this tool specifically:

- **Level 1 (default)**: audit + report, no ledger write required to view
  a report, but ledger write should happen automatically on every run
  regardless of level — the ledger is a passive record, not an automation
  step, and recording a `keep` verdict is not a cleanup action.
- **Level 2**: report includes exact `brew uninstall` / `trash` commands
  as text for high-confidence redundant items. Not executed.
- **Level 3**: future. Typed-confirmation-gated execution of only the
  pre-approved (via ledger `decision.status: accepted`) removal batch,
  using `trash` (already in the user's brew list) rather than `rm -rf` —
  reversible by design.
- The alternatives engine operates independently of automation level and
  is **always** recommend-only, per the federation contract's rule 7 —
  this does not loosen at Level 3/4.

---

## Scope: v0.2 Build Objective

Build **mac-app-audit v0.2 — Ledger-Native Collector + Deterministic
Scoring + Delta Mode**.

Primary objective:

> The collector produces deterministic usage scores (including shell
> history for CLI tools) and writes valid federation-schema ledger
> entries; the skill consumes the ledger instead of re-deriving
> everything from scratch each run; a `--delta` mode produces a
> two-minute weekly briefing instead of a full report.

Secondary objective:

> The redundancy-cluster pass and alternatives-engine rotation queue are
> both implemented and demonstrably working against the real inventory
> already captured in `mac_apps_report.txt` (present in this repo's
> `tests/fixtures/` — reuse it, don't ask the user to regenerate it for
> every test).

### In scope for v0.2

1. Extend `scripts/collect_inventory.sh` (or add a new
   `scripts/collect_usage_signals.sh` — agent's call on whether to extend
   vs. split, but keep `collect_inventory.sh`'s existing output shape
   backward compatible) to parse `~/.zsh_history` retroactively for CLI
   tool invocation counts over a configurable lookback window (default 90
   days), and to compute `is_leaf` + dependent-count from `brew deps
   --installed` / `brew uses --installed`.
2. A ledger writer (`scripts/write_ledger.py` or equivalent) that takes
   the collector's JSON output plus the agent's classification decisions
   and emits entries conforming to
   `../mac-tools-federation/schema/ledger-entry.schema.json`. Must call
   the federation repo's `validate_ledger.py` as a post-write check and
   fail loudly if any entry doesn't validate — never write an invalid
   ledger.
3. `entry_id` derivation exactly as specified in the federation
   `CONVENTIONS.md` (`sha256(producer + ":" + subject.identifier)[:16]`)
   so re-runs update `updated_at` on existing entries rather than
   duplicating them.
4. A `--delta` mode for the skill/command: reads the existing ledger,
   diffs against current `brew list` + `.app` scan for new installs,
   surfaces any entry with `decision.status: deferred` whose
   `revisit_after` date has passed, and runs the alternatives-engine
   rotation queue (5 tools, oldest-`last_verified`-first) for that week
   only. Produces a short report, not the full categorized table.
5. A `user_stack_profile.json` (or `.toml`, match FreeUp's config style
   for consistency) capturing hardware (Apple Silicon, unified memory
   size), primary languages, and known tool preferences — read by the
   alternatives engine for fit-checking. Seed it with what's already
   known from this project's history rather than leaving it a blank
   template.
6. Redundancy-cluster detection made concrete: implement the specific
   clusters already identified by inspection of the sample data (archive
   tools: keka/rar/p7zip/sevenzip; file managers: commander-one/marta;
   markdown editors: mark-text/markdown-preview/zettlr/obsidian/qlmarkdown;
   local-inference runners: ollama/LM Studio/Open WebUI/jan.ai/
   osaurus/oMLX/llama.cpp; Python version management: pyenv + multiple
   python@3.x formulae + anaconda cask + Python.app) as a starting
   pattern set in `SKILL.md`, not something the agent has to rediscover
   from nothing each run.
7. Tests: extend `tests/` with a smoke test that runs the full pipeline
   (fixture inventory → deterministic scoring → ledger write → federation
   validator) end to end without requiring a live Mac, using
   `tests/fixtures/sample_inventory.json` (add this fixture; derive it
   from the existing `mac_apps_report.txt` plus synthetic usage numbers).

### Not in scope for v0.2 (explicitly deferred, do not build yet)

- Actual removal execution (Level 3). Report/plan text only.
- Umbrella command spanning FreeUp Space. Blocked on FreeUp reaching its
  own ledger-writing milestone (its v0.6).
- GUI, background daemon, launchd job. The daily loop stays retroactive-
  read-only per decision #7 above — do not add a daemon even if it seems
  like a small step from here.
- `2.0.0` federation schema changes (e.g. a `superseded_by` field). Only
  revisit if v0.2's real usage against the current 1.0.0 schema surfaces
  an actual limitation, not preemptively.

---

## Files to Add or Update in v0.2

Add:
```text
scripts/collect_usage_signals.sh   (or extend collect_inventory.sh — agent's call, document the choice)
scripts/write_ledger.py
scripts/user_stack_profile.json
tests/fixtures/sample_inventory.json
tests/test_ledger_pipeline.py
```

Update:
```text
SKILL.md          — add ledger read/write steps, concrete redundancy-cluster
                     pattern set, rotation-queue logic, --delta mode behavior
commands/audit-apps.md  — add a --delta variant or a second command file
README.md         — document ledger location, federation repo dependency,
                     and the --delta usage pattern
```

Avoid changing:
```text
The federation repo (mac-tools-federation) itself — this repo consumes
its schema/contract, never edits it. If v0.2 work reveals the schema
needs a change, propose it there separately; don't fork a local copy.
```

---

## Acceptance Criteria

The v0.2 implementation is done when:

```bash
bash -n scripts/collect_inventory.sh
bash -n scripts/collect_usage_signals.sh   # if added as separate file
python3 -m py_compile scripts/write_ledger.py
python3 -m py_compile tests/test_ledger_pipeline.py
python3 tests/test_ledger_pipeline.py
python3 ../mac-tools-federation/validator/validate_ledger.py <path-to-generated-test-ledger>
```

all pass, and:

```bash
python3 scripts/write_ledger.py --input tests/fixtures/sample_inventory.json --output /tmp/mac-app-audit-test.ledger.json
```

produces a ledger that validates cleanly, contains at least one entry per
verdict type represented in the sample fixture, and correctly derives
`entry_id` such that running the command twice on unchanged input produces
identical `entry_id`s with only `updated_at` differing.

Also verify manually (requires a real Mac, not this sandbox):

```bash
chmod +x scripts/collect_inventory.sh
./scripts/collect_inventory.sh > app_inventory.json
# then, via Claude Code or Codex:
/audit-apps
/audit-apps --delta
```

Expected: full run produces a categorized report plus a valid ledger file
at the federation-specified location; delta run completes in well under a
minute and surfaces only what changed since the last run.

---

## Git Rules

1. Run initial validation before editing.
2. Make scoped changes only — this handoff's v0.2 scope, not the deferred
   items.
3. Run full validation after editing.
4. Remove `__pycache__` and temporary files.
5. Show `git diff --stat`.
6. Commit only when tests pass.
7. Use clear commit messages.
8. Do not push unless explicitly asked.

Suggested commit message for v0.2:
```text
Add ledger-native collector, deterministic usage scoring, and delta mode
```

---

## Exact First Prompt (Claude Code or Codex)

Paste this from the local repo root, with `mac-tools-federation` cloned as
a sibling directory:

```text
Read HANDOFF_v0.1.md, SKILL.md, README.md, and
../mac-tools-federation/README.md, SAFETY_CONTRACT.md, CONVENTIONS.md,
and schema/ledger-entry.schema.json.

Implement mac-app-audit v0.2 per HANDOFF_v0.1.md's Scope section exactly.

Do not implement anything listed under "Not in scope for v0.2."
Do not modify the mac-tools-federation repo.
Preserve the existing collect_inventory.sh output shape for backward
compatibility.
Preserve the redundancy-cluster and verdict-taxonomy design already
specified in SKILL.md — extend it, don't redesign it.

Required behavior:
- scripts/write_ledger.py produces entries that validate against
  ../mac-tools-federation/schema/ledger-entry.schema.json
- entry_id is derived deterministically per CONVENTIONS.md
- A --delta mode exists and completes without a full re-categorization pass
- user_stack_profile.json is seeded with the known hardware/language
  context from HANDOFF_v0.1.md, not left as a blank template
- Rejected ledger entries with a decision.reason suppress re-suggestion of
  that specific change on subsequent runs

Validation:
- bash -n scripts/collect_inventory.sh
- python3 -m py_compile scripts/write_ledger.py
- python3 tests/test_ledger_pipeline.py
- python3 ../mac-tools-federation/validator/validate_ledger.py against a
  generated test ledger

After editing:
- Remove __pycache__ and temporary files.
- Show git diff --stat.
- Summarize changed files and key design choices.
- Commit with message: Add ledger-native collector, deterministic usage
  scoring, and delta mode
- Do not push.
```

---

## Product Evaluation Prompt After v0.2

```text
Product-test the current app as if you are the repo owner running it
weekly for six months.

Do not modify files.

Run the full pipeline against tests/fixtures/sample_inventory.json, then
simulate a second run with one entry's decision.status set to "rejected"
with a reason, and confirm the suppression behavior works.

Then evaluate:
1. Does the --delta mode actually feel like a two-minute read, or does it
   still surface too much?
2. Does the redundancy-cluster pass catch the patterns already specified
   in SKILL.md against the real sample data?
3. Is the alternatives-engine rotation queue logic sound, or does it risk
   never reaching low-usage-but-still-relevant tools?
4. What's still confusing?
5. What's the next highest-value enhancement — and does it belong in this
   repo or is it actually FreeUp Space / federation-level scope creep?

Do not run any removal or execution commands.
```

---

## Summary

Build order:

```text
1. Deterministic usage-signal collection (shell history + dependency graph)
2. Ledger writer + federation schema validation in the loop
3. Delta mode
4. Concrete redundancy-cluster pattern set in SKILL.md
5. Alternatives-engine rotation queue against user_stack_profile
6. Tests proving the rejected-with-reason suppression actually works
7. Only later: Level 3 approved execution, umbrella command, schema v2
```

The product wins when the user feels: *this remembers what I decided last
time, tells me what changed, and never makes me re-explain myself.*
