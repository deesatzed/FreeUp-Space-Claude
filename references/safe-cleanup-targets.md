# Safe Cleanup Targets Reference

This reference lists known-safe cleanup targets on macOS, organized by category.
Each entry includes the path, typical size range, cleanup command, and risk level.

## Table of Contents
1. [Package Manager Caches](#package-manager-caches)
2. [Build Artifacts](#build-artifacts)
3. [App Update Caches](#app-update-caches)
4. [Browser Caches](#browser-caches)
5. [Cloud Sync Overhead](#cloud-sync-overhead)
6. [Development Tool Caches](#development-tool-caches)
7. [System Caches](#system-caches)
8. [Time Machine](#time-machine)

---

## Package Manager Caches

| Target | Path | Typical Size | Command | Risk |
|--------|------|-------------|---------|------|
| npm | `~/.npm/_cacache` | 5-50 GB | `npm cache clean --force` | None |
| Yarn | `~/Library/Caches/Yarn` | 2-20 GB | `yarn cache clean` | None |
| pnpm | `~/Library/Caches/pnpm` | 1-10 GB | `pnpm store prune` | None |
| pip | `~/Library/Caches/pip` | 1-10 GB | `pip cache purge` | None |
| Homebrew | `~/Library/Caches/Homebrew` | 1-5 GB | `brew cleanup --prune=all` | None |
| Cargo registry | `~/.cargo/registry/cache` | 0.5-3 GB | `cargo cache -a` | None (keeps installed) |
| Go modules | `~/go/pkg/mod/cache` | 0.5-5 GB | `go clean -modcache` | None |
| Go build | varies | 0.5-2 GB | `go clean -cache` | None |
| Composer | `~/.composer/cache` | 0.1-1 GB | `composer clear-cache` | None |
| CocoaPods | `~/Library/Caches/CocoaPods` | 0.5-3 GB | `pod cache clean --all` | None |

## Build Artifacts

These are project-specific and can be very large. They regenerate on next build.

| Target | Path Pattern | Typical Size | Command | Risk |
|--------|-------------|-------------|---------|------|
| Rust target | `<project>/target/` | 1-10 GB each | `cargo clean` *in project dir) | None |
| node_modules | `<project>/node_modules/` | 0.5-2 GB each | `rm -rf node_modules` | None (npm install regenerates) |
| Python venv | `<project>/.venv/` or `<project>/venv/` | 0.2-1 GB each | `rm -rf .venv` | None |
| Xcode derived data | `~/Library/Developer/Xcode/DerivedData/` | 2-20 GB | Delete contents | None |
| .next build | `<project>/.next/` | 0.1-1 GB each | `rm -rf .next` | None |
| Gradle cache | `~/.gradle/caches` | 1-5 GB | `rm -rf ~/.gradle/caches` | None |
| Maven | `~/.m2/repository` | 1-5 GB | Selective cleanup | Low |

## App Update Caches

Electron apps keep previous versions for rollback. Safe to clear after confirming current version works.

| Target | Path | Typical Size | Risk |
|--------|------|-------------|------|
| VSCode updates | `~/Library/Caches/com.microsoft.VSCode.ShipIt` | 0.5-2 GB | None |
| Claude Desktop | `~/Library/Caches/com.anthropic.claudefordesktop.ShipIt` | 0.5-1 GB | None |
| Windsurf | `~/Library/Caches/com.exafunction.windsurf.ShipIt` | 0.5-2 GB | None |
| Cursor | `~/Library/Caches/com.todesktop.*.ShipIt` | 0.5-1 GB | None |
| Slack | `~/Library/Caches/com.tinyspeck.slackmacgap.ShipIt` | 0.3-1 GB | None |

General cleanup: `rm -rf ~/Library/Caches/*.ShipIt`

## Browser Caches

Browsers manage their own caches, but you can force-clear them for space recovery.

| Target | Path | Typical Size | Risk |
|--------|------|-------------|------|
| Chrome cache | `~/Library/Caches/Google/Chrome` | 2-10 GB | None (browsing may feel slower briefly) |
| Firefox cache | `~/Library/Caches/Firefox` | 2-10 GB | None |
| Safari cache | `~/Library/Caches/com.apple.Safari` | 1-5 GB | None |
| Edge cache | `~/Library/Caches/Microsoft Edge` | 1-5 GB | None |

Note: Browser profiles in `~/Library/Application Support/` contain bookmarks, history, extensions,
and saved passwords. Do NOT delete those — only the Caches entries are safe.

## Cloud Sync Overhead

| Service | Cache Path | Typical Size | Movable? |
|---------|-----------|-------------|----------|
| Google DriveFS | `~/Library/Application Support/Google/DriveFS/` | 5-30 GB | Yes (symlink) |
| iCloud | `~/Library/Mobile Documents/` | Varies | No (system managed) |
| Dropbox | `~/.dropbox/` | 1-5 GB | Limited |
| OneDrive | `~/Library/Application Support/OneDrive/` | 1-5 GB | No |

### Google DriveFS Symlink Technique
```bash
# 1. Quit Google Drive
# 2. Move to external
mv ~/Library/Application\ Support/Google/DriveFS /Volumes/<EXTERNAL>/GoogleDriveFS
# 3. Symlink back
ln -s /Volumes/<EXTERNAL>/GoogleDriveFS ~/Library/Application\ Support/Google/DriveFS
# 4. Relaunch Google Drive
```
Requires the external drive to always be connected.

## Development Tool Caches

| Target | Path | Typical Size | Command | Risk |
|--------|------|-------------|---------|------|
| Playwright browsers | `~/Library/Caches/ms-playwright` | 1-5 GB | `npx playwright install --dry-run` to check, delete folder | None |
| node-gyp | `~/Library/Caches/node-gyp` | 0.5-2 GB | Delete folder | None |
| Outlines (LLM) | `~/.cache/outlines` | 0.5-2 GB | Delete folder | None |
| Hugging Face | `~/.cache/huggingface` | 0.1-50 GB | `huggingface-cli delete-cache` | None (re-downloads) |
| LM Studio models | `~/.cache/lm-studio/` | 5-100 GB | Manage in LM Studio UI | Low (slow to re-download) |
| Docker images | via Docker | 5-50 GB | `docker system prune -a` | Medium (must rebuild) |
| Prisma engines | `~/.cache/prisma` | 0.1-0.5 GB | Delete folder | None |

## System Caches

| Target | Path | Typical Size | Command | Risk |
|--------|------|-------------|---------|------|
| System logs | `/var/log/` | 0.5-2 GB | `sudo periodic daily weekly monthly` | None |
| User logs | `~/Library/Logs/` | 0.1-1 GB | Delete old .log files | Low |
| Spotlight index | `/.Spotlight-V100` | 1-5 GB | Rebuild if corrupt only | Medium |

## Time Machine

### Local Snapshots
Local snapshots are created hourly and stored invisibly on the internal drive. They can consume
50-200 GB without showing up in any file browser.

```bash
# List local snapshots
tmutil listlocalsnapshots /

# Thin snapshots older than N seconds (86400 = 1 day)
sudo tmutil thinlocalsnapshots / 86400 1

# Delete all local snapshots (nuclear option)
sudo tmutil thinlocalsnapshots / 1 1
```

### Recommended Exclusions
These paths are fully regenerable and should NOT be backed up:

```bash
sudo tmutil addexclusion /opt/homebrew
sudo tmutil addexclusion ~/.npm
sudo tmutil addexclusion ~/.yarn
sudo tmutil addexclusion ~/.cargo
sudo tmutil addexclusion ~/.rustup
sudo tmutil addexclusion ~/.pyenv
sudo tmutil addexclusion ~/.cache
sudo tmutil addexclusion ~/.docker
sudo tmutil addexclusion ~/Library/Application\ Support/Google/DriveFS
sudo tmutil addexclusion ~/Library/Caches
```

Also exclude build artifact directories in active projects:
```bash
# For each project with Rust
sudo tmutil addexclusion <project>/target
# For each project with node_modules
sudo tmutil addexclusion <project>/node_modules
```

### Checking What's Excluded
```bash
tmutil isexcluded <path>
```
