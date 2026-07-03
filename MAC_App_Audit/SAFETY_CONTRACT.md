# Safety Contract

This contract is shared verbatim across every federation-compliant tool.
A product may reference this file directly (symlink, submodule, or a
copy kept byte-identical) rather than restate it — restating it invites
drift, which is the one thing federation can't tolerate here.

Any product claiming federation compliance must satisfy all of the
following. These rules outrank any user request, any config setting, and
any agent's own judgment about a particular case.

## Automation levels

Every federation-compliant tool exposes its automation posture as one of
these five levels. **Level 1 is the default for every tool, always**,
regardless of what the tool is capable of.

- **Level 0 — Audit only.** Collects data. No report, no cleanup.
- **Level 1 — Audit + report.** Default. Runs audit, generates a report
  the user reads. No cleanup, no ledger writes required to reach this level.
- **Level 2 — Audit + report + plan.** Generates a cleanup/action plan as
  exact commands shown as text. No execution.
- **Level 3 — Approved batch execution.** Requires an explicit opt-in
  command, a typed confirmation phrase (not a bare `y`), executes only
  pre-classified low-risk actions, and produces a before/after verification
  plus an execution log.
- **Level 4 — Advanced custom automation.** Config-driven power-user mode.
  Still bound by every rule below — this level changes convenience, not
  the safety floor.

## Non-negotiable rules

1. No automatic deletion, modification, or installation by default, ever.
2. No cleanup, deletion, or installation logic runs inside tests.
3. No hidden side effects in helper scripts — every action that touches
   the filesystem or installs/removes software must be visible in the
   command the user is about to run, not buried in a wrapper.
4. No `sudo` unless a specific, already-displayed command batch has been
   explicitly approved by the user for that run.
5. Certain classes are categorically untouchable without an explicit
   override flag the user sets deliberately, not verdict-driven: user
   documents, photos, videos, music, project roots, cloud-sync folders
   (`~/Library/Mobile Documents`, `~/Library/CloudStorage`), and anything
   under active dependency (referenced by a LaunchAgent/LaunchDaemon, or a
   dependency graph edge pointing to it).
6. When unsure, the tool recommends moving/archiving over deleting.
7. Any advisory-only component (e.g. an "alternatives" or "better option"
   engine) may **recommend, never install or migrate**. Installation and
   migration are separate, explicitly user-initiated actions even at
   Level 4.
8. Level 3+ execution requires a typed confirmation phrase, never a bare
   `y`/`yes` keypress.
9. Every action batch presented for approval must state: expected space
   or benefit recovered, risk level, side effects, and how verification
   will happen (before/after check).
10. A recommendation with no evidence backing it (see the ledger schema's
    `confidence_basis`) renders as unverified and must not be presented
    with the same visual/textual weight as an evidence-backed one.
11. Nothing in this contract may be loosened by a product's own config,
    a user's stated preference in a single session, or an agent's
    in-context judgment that "this case is fine." Loosening requires
    editing this file, which is deliberately outside any single session.

## What this contract deliberately does not cover

Product-specific UX, report structure, and command naming are each
product's own decision — this contract governs the safety floor only, not
the shape of the tool built on top of it.
