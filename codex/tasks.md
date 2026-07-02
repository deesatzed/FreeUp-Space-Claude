# Codex Task Packs

Use these as focused prompts for Codex. Each pack should be completed in its own PR unless the changes are tiny.

## Task Pack 1 — Improve Report Ranking

**Goal:** Make `scripts/generate_report.py` produce a more useful ranked report from existing text audit output.

Requirements:

- Parse every section that contains `du -sh` style lines.
- Create a unified top findings table ranked by size.
- Add columns: path, size, category, risk, recommended action.
- Preserve the current sections for disk overview, Time Machine snapshots, caches, applications, and exclusions.
- Never execute cleanup commands.
- Update `tests/smoke_test.py` and fixture expectations.

Validation:

```bash
python3 -m py_compile scripts/generate_report.py
python3 tests/smoke_test.py
```

## Task Pack 2 — Add Structured JSON Audit Output

**Goal:** Add a machine-readable audit format without removing the existing text format.

Requirements:

- Add an optional `--json` mode or a second script.
- Capture path, size, category, source section, and status (`ok`, `missing`, `unreadable`, `skipped`).
- Keep live audit read-only.
- Make report generation prefer JSON when supplied.
- Add a JSON fixture and tests.

Validation:

```bash
bash -n scripts/disk_audit.sh
python3 -m py_compile scripts/generate_report.py
python3 tests/smoke_test.py
```

## Task Pack 3 — Interactive Wrapper

**Goal:** Add a safe command-line wrapper for non-agent users.

Requirements:

- Create `scripts/freeup_space.py`.
- Ask setup questions: symptom, external drives, primary use, comfort level.
- Run the read-only audit.
- Generate a Markdown report.
- Print report path and top recommendations.
- Do not execute cleanup commands.

Validation:

```bash
python3 -m py_compile scripts/freeup_space.py
python3 tests/smoke_test.py
```

## Task Pack 4 — Claude Skill Packaging

**Goal:** Make the repo easier to package as a Claude skill.

Requirements:

- Define a repeatable packaging command.
- Include `SKILL.md`, scripts, references, and evals.
- Exclude `.git`, test artifacts, caches, and temporary files.
- Document install steps in README.

Validation:

```bash
bash -n scripts/package_skill.sh
```

## Task Pack 5 — macOS-Specific Coverage Expansion

**Goal:** Add high-yield macOS cleanup discovery targets without increasing risk.

Candidate additions:

- Xcode DerivedData and Archives
- iOS device backups
- Simulator runtimes/devices
- Homebrew cache and Cellar size
- Hugging Face / LM Studio model caches
- Cursor/Windsurf/VS Code extension and update caches
- Apple Mail downloads
- Messages attachments

Requirements:

- Audit only.
- Categorize each target by safety/risk.
- Never add automatic deletion.
- Update `references/safe-cleanup-targets.md`.
