#!/bin/bash
# Mac Disk Audit Script
# Generates a comprehensive disk usage report in text format.
# Designed to be run by an assistant with explicit user approval, or directly in Terminal.
#
# Usage: bash scripts/disk_audit.sh [output_file]
# If no output file is specified, prints to stdout.
#
# Safety contract:
# - Read-only audit only.
# - No cleanup, delete, move, or sudo operations.
# - Missing optional tools/paths are reported and do not abort the audit.

set -uo pipefail
shopt -s nullglob

OUTPUT="${1:-/dev/stdout}"

section() {
    printf '\n--- %s ---\n' "$1" >> "$OUTPUT"
}

note() {
    printf '%s\n' "$1" >> "$OUTPUT"
}

run_optional() {
    local label="$1"
    shift
    note "# $label"
    "$@" >> "$OUTPUT" 2>/dev/null || note "SKIPPED: $label unavailable or not permitted"
}

du_path() {
    local path="$1"
    if [ -e "$path" ]; then
        du -sh "$path" >> "$OUTPUT" 2>/dev/null || note "UNREADABLE: $path"
    else
        note "MISSING: $path"
    fi
}

top_children_by_size() {
    local dir="$1"
    local limit="$2"

    if [ ! -d "$dir" ]; then
        note "MISSING: $dir"
        return 0
    fi

    for path in "$dir"/*; do
        [ -e "$path" ] || continue
        du -sk "$path" 2>/dev/null
    done | sort -rn | head -"$limit" | while IFS= read -r line; do
        path="$(printf '%s' "$line" | sed 's/^[0-9][0-9]*[[:space:]]*//')"
        du_path "$path"
    done
}

top_glob_by_size() {
    local pattern="$1"
    local limit="$2"

    # shellcheck disable=SC2086
    for path in $pattern; do
        [ -e "$path" ] || continue
        du -sk "$path" 2>/dev/null
    done | sort -rn | head -"$limit" | while IFS= read -r line; do
        path="$(printf '%s' "$line" | sed 's/^[0-9][0-9]*[[:space:]]*//')"
        du_path "$path"
    done
}

printf '=== DISK AUDIT %s ===\n' "$(date '+%Y-%m-%d %H:%M:%S')" > "$OUTPUT"

section "DISK OVERVIEW"
run_optional "df -h /" df -h /

section "APFS VOLUMES"
BOOT_DISK="$(diskutil info / 2>/dev/null | awk -F: '/Part of Whole/ {gsub(/^[ \t]+/, "", $2); print $2; exit}')"
if [ -n "$BOOT_DISK" ]; then
    diskutil apfs list "$BOOT_DISK" >> "$OUTPUT" 2>/dev/null || diskutil apfs list >> "$OUTPUT" 2>/dev/null || note "SKIPPED: APFS details unavailable"
else
    diskutil apfs list >> "$OUTPUT" 2>/dev/null || note "SKIPPED: APFS details unavailable"
fi

section "TIME MACHINE LOCAL SNAPSHOTS"
SNAPSHOTS="$(tmutil listlocalsnapshots / 2>/dev/null || true)"
if [ -n "$SNAPSHOTS" ]; then
    printf '%s\n' "$SNAPSHOTS" >> "$OUTPUT"
else
    note "No local snapshots reported, or tmutil unavailable/not permitted."
fi
SNAPSHOT_COUNT="$(printf '%s\n' "$SNAPSHOTS" | grep -c 'com.apple' || true)"
note "Snapshot count: $SNAPSHOT_COUNT"

section "TIME MACHINE DESTINATION"
run_optional "tmutil destinationinfo" tmutil destinationinfo

section "TIME MACHINE EXCLUSION STATUS"
for p in /opt/homebrew "$HOME/.npm" "$HOME/.yarn" "$HOME/.cargo" "$HOME/.rustup" "$HOME/.pyenv" "$HOME/.cache" "$HOME/.docker"; do
    if [ -e "$p" ]; then
        tmutil isexcluded "$p" >> "$OUTPUT" 2>/dev/null || note "SKIPPED: tmutil exclusion check for $p"
    else
        note "MISSING: $p"
    fi
done

section "USER DIRECTORIES"
for d in "$HOME/Library" "$HOME/Downloads" "$HOME/Desktop" "$HOME/Documents" "$HOME/Movies" "$HOME/Music" "$HOME/Pictures" "$HOME/Projects"; do
    du_path "$d"
done

section "SYSTEM DIRECTORIES"
for d in /Applications /opt/homebrew /Library/Developer; do
    du_path "$d"
done

section "HIDDEN DOT-FOLDERS"
for d in "$HOME/.npm" "$HOME/.yarn" "$HOME/.cargo" "$HOME/.rustup" "$HOME/.pyenv" "$HOME/.cache" "$HOME/.docker" "$HOME/.local" "$HOME/.pnpm-store" "$HOME/.bun"; do
    du_path "$d"
done

section "LIBRARY CACHES (TOP 20)"
top_children_by_size "$HOME/Library/Caches" 20 >> "$OUTPUT"

section "APPLICATION SUPPORT (TOP 15)"
top_children_by_size "$HOME/Library/Application Support" 15 >> "$OUTPUT"

section "APPLICATIONS BY SIZE (TOP 15)"
top_glob_by_size "/Applications/*.app" 15 >> "$OUTPUT"

section "CONTAINERS"
du_path "$HOME/Library/Containers"

section "DOWNLOADS (TOP 15)"
top_children_by_size "$HOME/Downloads" 15 >> "$OUTPUT"

section "CLOUD SYNC"
note "Google Drive:"
du_path "$HOME/Library/Application Support/Google/DriveFS"
if [ -d "$HOME/Library/CloudStorage" ]; then
    ls "$HOME/Library/CloudStorage" >> "$OUTPUT" 2>/dev/null || note "UNREADABLE: $HOME/Library/CloudStorage"
else
    note "MISSING: $HOME/Library/CloudStorage"
fi
note ""
note "iCloud:"
du_path "$HOME/Library/Mobile Documents"
note ""
note "Dropbox:"
du_path "$HOME/.dropbox"

section "DOCKER"
du_path "$HOME/.docker"
run_optional "docker system df" docker system df

note ""
note "=== AUDIT COMPLETE ==="
