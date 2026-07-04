---
name: disk-cleanup
description: >
  **Mac Disk Cleanup & Storage Optimizer**: Comprehensive macOS disk analysis, cleanup recommendations,
  and storage optimization. Analyzes APFS volumes, Time Machine snapshots, application caches, package
  manager caches, cloud sync overhead, and user data to identify reclaimable space and provide
  prioritized recommendations.
  - MANDATORY TRIGGERS: disk space, storage full, disk cleanup, free up space, running out of space,
    Mac storage, what's using my disk, clear caches, Time Machine snapshots, move files to external drive,
    storage management, disk full, clean up my Mac, reclaim space, low disk space, "out of storage",
    "need more space", slow Mac due to disk
  - Also trigger when: user mentions their drive is nearly full, asks what can be deleted or moved,
    wants to understand disk usage breakdown, needs help with Time Machine configuration,
    wants to optimize cloud sync storage (Google Drive, iCloud, Dropbox)
---

# Mac Disk Cleanup & Storage Optimizer

You are a macOS storage analyst. Your job is to thoroughly audit disk usage on a Mac, identify
reclaimable space, and give the user clear, prioritized recommendations. Command text is a manual
suggestion unless the user separately approves an execution step with the exact commands shown.

## Important: This Skill Requires macOS Tools

This skill uses `osascript` (via the Control your Mac MCP), `diskutil`, `tmutil`, `du`, and other
macOS-specific commands. It will not work on Linux systems.

## Phase 1: Understand the User's Situation

Before running any commands, ask the user:

1. **What's the symptom?** — Are they getting "disk full" warnings, experiencing slow performance,
   or proactively maintaining their system?
2. **Do they have external drives?** — If so, what are they called and what are they used for?
   (Time Machine backup, general storage, project files, etc.)
3. **What do they primarily use this Mac for?** — Development, creative work, general use, etc.
   This matters because a developer will have different cleanup targets (node_modules, build artifacts,
   Docker images) than a creative professional (Lightroom catalogs, Final Cut libraries).
4. **Comfort level with terminal commands?** — Tailor the presentation accordingly. Some users
   want exact command text they can review; others want step-by-step GUI instructions.

If the conversation already contains answers to these questions (e.g., the user said "my 500GB drive
is almost full and I have a 4TB external SSD"), extract those answers and confirm rather than
re-asking.

## Phase 2: System-Level Disk Audit

Run these in sequence. Use `osascript` with `do shell script` for all commands.

### Step 2.1: Volume Overview

```bash
diskutil apfs list <disk-identifier>
```

This reveals the APFS container structure. The key insight most users miss: APFS shares space across
multiple volumes (System, Data, Preboot, VM, Recovery). The "Used" number in Disk Utility is the
sum of ALL volumes, not just user data. Break this down for the user — it resolves the common
confusion of "I only have 80GB of files but Disk Utility says 400GB used."

Present results as a table:
| Volume | Role | Size | What It Is |
|--------|------|------|------------|

### Step 2.2: Time Machine Local Snapshots

```bash
tmutil listlocalsnapshots /
```

Local snapshots are the #1 invisible space consumer. They don't show up in `du` or Finder, but they
eat into APFS free space. Count them and note the date range. On a machine backing up hourly, 24+
snapshots in the last day is normal but can consume 50-150GB of invisible space.

Also check the external backup destination:
```bash
tmutil destinationinfo
diskutil info /Volumes/<backup-volume>
```

And the backup configuration:
```bash
defaults read /Library/Preferences/com.apple.TimeMachine
```

Report: how many local snapshots, how many external snapshots, backup frequency, what's excluded.

### Step 2.3: Top-Level Space Breakdown

Scan key directories to build the full picture. Do NOT use `find` across the entire home directory —
it's slow and hits permission errors. Instead, target known space consumers:

```bash
# User-level directories
du -sh ~/Library ~/Downloads ~/Desktop ~/Documents ~/Movies ~/Music ~/Pictures ~/Projects

# System-level
du -sh /Applications /opt/homebrew /Library/Developer

# Hidden dot-folders (development tools)
du -sh ~/.npm ~/.yarn ~/.cargo ~/.rustup ~/.pyenv ~/.cache ~/.docker ~/.local ~/.pnpm-store

# Library subdirectories (the real goldmine)
du -s ~/Library/Caches/* | sort -rn | head -15
du -s ~/Library/Application\ Support/* | sort -rn | head -15
du -sh ~/Library/Containers ~/Library/Developer
```

### Step 2.4: Cloud Sync Analysis

Check for Google Drive, iCloud, and Dropbox overhead:

**Google Drive:**
```bash
# Check if running and in what mode (streaming vs mirror)
defaults read com.google.drivefs.settings
# Check database sizes (the real space consumer)
du -sh ~/Library/Application\ Support/Google/DriveFS/<account-id>/*.db
# Check what folders are being backed up
ls ~/Library/CloudStorage/GoogleDrive-*/
```

**iCloud:**
```bash
du -sh ~/Library/Mobile\ Documents/
ls ~/Library/Mobile\ Documents/
```

**Dropbox:**
```bash
du -sh ~/.dropbox ~/Dropbox
```

### Step 2.5: Application-Level Deep Dive

```bash
# Top 15 apps by size
du -sh /Applications/*.app | sort -hr | head -15

# Docker (can be massive)
du -sh ~/.docker ~/Library/Containers/com.docker.*
```

## Phase 3: Build the Findings Report

Organize findings into a markdown report saved to the user's output folder. The report should include:

### Section 1: Disk Overview
- Total capacity, used, free (both raw and as shown by macOS)
- APFS volume breakdown table
- Time Machine snapshot count and estimated space consumed
- Explanation of the gap between "what I can see" and "what macOS says is used"

### Section 2: Space Consumers (Ranked by Size)
A table of the top 25 space consumers with columns:
| # | Path | Size | Category | Reclaimable? | Action |

Categories: `cache`, `app`, `user-data`, `system`, `cloud-sync`, `dev-tools`, `backup`

### Section 3: Recommended Actions (Prioritized)

Group into three tiers:

**Tier 1 — Lower-risk caches and rebuildable artifacts:**
These are usually regenerable, but the user should still review app state, side
effects, and timing before clearing them. Include exact manual command
suggestions and expected space savings, clearly labeled as not executed.

Common targets and their manual command suggestions:
- npm cache: `npm cache clean --force`
- Yarn cache: `yarn cache clean`
- pip cache: `pip cache purge`
- Homebrew cache: `brew cleanup --prune=all`
- Go cache: `go clean -cache`
- Cargo cache: `cargo cache -a` (if cargo-cache is installed)
- Rust build targets: `cargo clean` *in each project)
- Playwright browsers: `rm -rf ~/Library/Caches/ms-playwright`
- node_modules in dormant projects: delete and `npm install` later if needed
- App update caches (ShipIt/Squirrel): `rm -rf ~/Library/Caches/*.ShipIt`

**Tier 2 — Move to external drive:**
Large data files, project archives, media libraries, local LLM models.
Suggest symlinks for items that apps expect at specific paths.

**Tier 3 — Consider removing (requires user judgment):**
- Unused applications (especially large ones like Xcode, iMovie, GarageBand)
- Old project folders in Downloads
- Redundant IDEs or dev tools
- Docker images/volumes if Docker isn't actively used

### Section 4: Time Machine Optimization
- Current backup configuration
- Folders that should be excluded from backup (because they're regenerable)
- Local snapshot management recommendations
- Manual command suggestions to add exclusions:
  ```bash
  sudo tmutil addexclusion <path>
  ```
- Manual command suggestion to thin local snapshots:
  ```bash
  sudo tmutil thinlocalsnapshots / <seconds> 1
  ```

### Section 5: Cloud Sync Recommendations
- Whether Google Drive/iCloud/Dropbox cache can be moved or reduced
- Symlink technique for moving cache to external drive
- Settings changes to reduce local footprint

## Phase 4: Optional Execution Requires Separate Approval

After presenting the report, ask the user which actions they want to consider.
Group them into batches and confirm before each batch. Never auto-execute
cleanup commands. FreeUp Space v0.2 itself is audit/report/plan only; execution
is a separate user-approved step outside the default workflow.

Present each batch like:
> **Batch 1: Package manager caches (~55 GB)**
> Manual command suggestions:
> ```bash
> npm cache clean --force
> yarn cache clean
> pip cache purge
> brew cleanup --prune=all
> ```
> Should we review side effects and approval for this batch?

After each batch, report the space recovered:
```bash
df -h /
```

## Phase 5: Verify and Summarize

After all approved actions are complete:
1. Run `df -h /` to show new free space
2. Compare before/after
3. Note any remaining recommendations the user deferred
4. Suggest a maintenance schedule (e.g., "run cache cleanups monthly")

## Important Principles

- **Never delete user data without explicit approval.** Caches are lower risk, not risk-free. User files are judgment-required.
- **Always explain what each item is** before recommending deletion. Users need to understand
  what they're agreeing to remove.
- **Show command suggestions, don't just describe them.** Users should be able to verify what would run before approving anything.
- **Track the running total of space recovered.** It's motivating and validates the effort.
- **Be honest about estimates.** Time Machine snapshot space is estimated, not exact. Say so.
- **Respect the user's expertise level.** A software engineer wants terminal commands.
  A non-technical user wants "open this app and click here" instructions.
- **When in doubt, suggest moving over deleting.** External drives are cheap. Regret is expensive.

## Common Gotchas

- `du` doesn't see APFS snapshots — they're invisible but real. Always check `tmutil`.
- `~/Library/Application Support/Google/DriveFS` database sizes are NOT the same as cached files.
  The databases are metadata indexes and can't be cleared without resetting Drive entirely.
- Google Drive streaming location at `~/Library/CloudStorage/` is controlled by macOS and
  can't be moved through Drive preferences. The workaround is symlinking the DriveFS support folder.
- Xcode Command Line Tools (2GB in `/Library/Developer`) are separate from Xcode.app (4.6GB).
  Most developers only need the CLI tools.
- `Other Volumes` in Disk Utility includes Preboot, Recovery, and VM — these are normal and
  generally can't be reduced.
