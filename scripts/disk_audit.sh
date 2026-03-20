#!/bin/bash
# Mac Disk Audit Script
# Generates a comprehensive disk usage report in JSON-ish format
# Designed to be run via osascript's `do shell script` or directly in terminal
#
# Usage: bash disk_audit.sh [output_file]
# If no output file specified, prints to stdout

set -euo pipefail

OUTPUT="${1:-/dev/stdout}"

echo "=== DISK AUDIT $(date '+%Y-%m-%d %H:%M:%S') ===" > "$OUTPUT"

# 1. Basic disk info
echo "" >> "$OUTPUT"
echo "--- DISK OVERVIEW ---" >> "$OUTPUT"
df -h / >> "$OUTPUT" 2>/dev/null

# 2. APFS container info
echo "" >> "$OUTPUT"
echo "--- APFS VOLUMES ---" >> "$OUTPUT"
BOOT_DISK=$(diskutil info / | grep "Part of Whole" | awk '{print $NF}')
if [ -n "$BOOT_DISK" ]; then
    diskutil apfs list "$BOOT_DISK" >> "$OUTPUT" 2>/dev/null
fi

# 3. Time Machine local snapshots
echo "" >> "$OUTPUT"
echo "--- TIME MACHINE LOCAL SNAPSHOTS ---" >> "$OUTPUT"
tmutil listlocalsnapshots / >> "$OUTPUT" 2>/dev/null
echo "" >> "$OUTPUT"
echo "Snapshot count: $(tmutil listlocalsnapshots / 2>/dev/null | grep -c 'com.apple' || echo 0)" >> "$OUTPUT"

# 4. Time Machine destination
echo "" >> "$OUTPUT"
echo "--- TIME MACHINE DESTINATION ---" >> "$OUTPUT"
tmutil destinationinfo >> "$OUTPUT" 2>/dev/null

# 5. Time Machine exclusions check
echo "" >> "$OUTPUT"
echo "--- TIME MACHINE EXCLUSION STATUS ---" >> "$OUTPUT"
for p in /opt/homebrew ~/.npm ~/.yarn ~/.cargo ~/.rustup ~/.pyenv ~/.cache ~/.docker; do
    tmutil isexcluded "$p" >> "$OUTPUT" 2>/dev/null
done

# 6. Top-level user directories
echo "" >> "$OUTPUT"
echo "--- USER DIRECTORIES ---" >> "$OUTPUT"
for d in ~/Library ~/Downloads ~/Desktop ~/Documents ~/Movies ~/Music ~/Pictures ~/Projects; do
    du -sh "$d" >> "$OUTPUT" 2>/dev/null
done

# 7. System directories
echo "" >> "$OUTPUT"
echo "--- SYSTEM DIRECTORIES ---" >> "$OUTPUT"
du -sh /Applications >> "$OUTPUT" 2>/dev/null
du -sh /opt/homebrew >> "$OUTPUT" 2>/dev/null
du -sh /Library/Developer >> "$OUTPUT" 2>/dev/null

# 8. Hidden dot-folders
echo "" >> "$OUTPUT"
echo "--- HIDDEN DOT-FOLDERS ---" >> "$OUTPUT"
for d in ~/.npm ~/.yarn ~/.cargo ~/.rustup ~/.pyenv ~/.cache ~/.docker ~/.local ~/.pnpm-store ~/.bun; do
    du -sh "$d" >> "$OUTPUT" 2>/dev/null
done

# 9. Library/Caches breakdown
echo "" >> "$OUTPUT"
echo "--- LIBRARY CACHES (TOP 20) ---" >> "$OUTPUT"
du -s ~/Library/Caches/* 2>/dev/null | sort -rn | head -20 | while read size path; do
    du -sh "$path" 2>/dev/null
done >> "$OUTPUT"

# 10. Application Support breakdown
echo "" >> "$OUTPUT"
echo "--- APPLICATION SUPPORT (TOP 15) ---" >> "$OUTPUT"
du -s "$HOME/Library/Application Support"/* 2>/dev/null | sort -rn | head -15 | while read size path; do
    du -sh "$path" 2>/dev/null
done >> "$OUTPUT"

# 11. Top apps by size
echo "" >> "$OUTPUT"
echo "--- APPLICATIONS BY SIZE (TOP 15) ---" >> "$OUTPUT"
du -sh /Applications/*.app 2>/dev/null | sort -hr | head -15 >> "$OUTPUT"

# 12. Containers
echo "" >> "$OUTPUT"
echo "--- CONTAINERS ---" >> "$OUTPUT"
du -sh ~/Library/Containers >> "$OUTPUT" 2>/dev/null

# 13. Downloads breakdown
echo "" >> "$OUTPUT"
echo "--- DOWNLOADS (TOP 15) ---" >> "$OUTPUT"
du -s ~/Downloads/* 2>/dev/null | sort -rn | head -15 | while read size path; do
    du -sh "$path" 2>/dev/null
done >> "$OUTPUT"

# 14. Cloud sync check
echo "" >> "$OUTPUT"
echo "--- CLOUD SYNC ---" >> "$OUTPUT"
echo "Google Drive:" >> "$OUTPUT"
du -sh "$HOME/Library/Application Support/Google/DriveFS" >> "$OUTPUT" 2>/dev/null
ls "$HOME/Library/CloudStorage/" >> "$OUTPUT" 2>/dev/null
echo "" >> "$OUTPUT"
echo "iCloud:" >> "$OUTPUT"
du -sh ~/Library/Mobile\ Documents/ >> "$OUTPUT" 2>/dev/null
echo "" >> "$OUTPUT"
echo "Dropbox:" >> "$OUTPUT"
du -sh ~/.dropbox >> "$OUTPUT" 2>/dev/null

# 15. Docker
echo "" >> "$OUTPUT"
echo "--- DOCKER ---" >> "$OUTPUT"
du -sh ~/.docker >> "$OUTPUT" 2>/dev/null
docker system df >> "$OUTPUT" 2>/dev/null

echo "" >> "$OUTPUT"
echo "=== AUDIT COMPLETE ===" >> "$OUTPUT"
