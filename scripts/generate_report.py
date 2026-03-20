#!/usr/bin/env python3
"""
Generate a Markdown disk cleanup report from audit data.

This script parses the output of disk_audit.sh and generates a formatted
Markdown report with prioritized recommendations.

Usage: python3 generate_report.py <audit_output_file> <report_output_file>
"""

import sys
import re
import os
from datetime import datetime


def parse_size_to_bytes(size_str):
    """Convert human-readable size (e.g., '4.6G', '898M', '12K') to bytes."""
    size_str = size_str.strip()
    multipliers = {
        'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4,
        'B': 1
    }
    match = re.match(r'([\d.]+)\s*([KMGTB])', size_str, re.IGNORECASE)
    if match:
        num = float(match.group(1))
        unit = match.group(2).upper()
        return int(num * multipliers.get(unit, 1))
    return 0


def bytes_to_human(num_bytes):
    """Convert bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def parse_du_lines(text):
    """Parse du output lines into (size_str, path) tuples."""
    results = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        match = re.match(r'([\d.]+[KMGTB]?)\s+(.*)', line, re.IGNORECASE)
        if match:
            results.append((match.group(1), match.group(2)))
    return results


def categorize_path(path):
    """Categorize a path into a cleanup category."""
    path_lower = path.lower()
    if '/caches/' in path_lower or '/.cache' in path_lower or '_cacache' in path_lower:
        return 'cache'
    if '/application support/' in path_lower:
        return 'app-data'
    if '.app' in path_lower or '/applications/' in path_lower:
        return 'app'
    if any(x in path_lower for x in ['.npm', '.yarn', '.cargo', '.rustup', '.pyenv', 'homebrew']):
        return 'dev-tools'
    if any(x in path_lower for x in ['google/drivefs', 'cloudstorage', 'dropbox', 'icloud']):
        return 'cloud-sync'
    if any(x in path_lower for x in ['/downloads/', '/documents/', '/desktop/', '/movies/', '/music/']):
        return 'user-data'
    return 'system'


def is_safe_to_clear(path):
    """Determine if a path is safe to clear without data loss."""
    safe_patterns = [
        '/Caches/', '/.cache/', '_cacache', '.ShipIt',
        'node_modules', '/target/debug', '/target/release',
        '.npm', 'yarn/cache', 'pip/cache', 'Homebrew/downloads',
    ]
    return any(p.lower() in path.lower() for p in safe_patterns)


def generate_report(audit_file, output_file):
    """Generate markdown report from audit data."""
    with open(audit_file, 'r') as f:
        content = f.read()

    report = []
    report.append(f"# Mac Disk Cleanup Report")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Parse disk overview
    if '--- DISK OVERVIEW ---' in content:
        section = content.split('--- DISK OVERVIEW ---')[1].split('---')[0]
        report.append("## Disk Overview")
        report.append("```")
        report.append(section.strip())
        report.append("```\n")

    # Parse snapshot count
    if 'Snapshot count:' in content:
        match = re.search(r'Snapshot count:\s*(\d+)', content)
        if match:
            count = int(match.group(1))
            report.append(f"### Time Machine Local Snapshots: **{count}**")
            if count > 10:
                report.append(f"> ⚠️ {count} local snapshots detected. These consume invisible disk space")
                report.append(f"> (typically 50-150 GB). Consider thinning with:")
                report.append(f"> `sudo tmutil thinlocalsnapshots / 86400 1`\n")

    # Parse user directories
    if '--- USER DIRECTORIES ---' in content:
        section = content.split('--- USER DIRECTORIES ---')[1].split('---')[0]
        entries = parse_du_lines(section)
        if entries:
            report.append("## Directory Sizes\n")
            report.append("| Directory | Size |")
            report.append("|-----------|------|")
            for size, path in entries:
                dirname = os.path.basename(path.rstrip('/'))
                report.append(f"| ~/{dirname} | {size} |")
            report.append("")

    # Parse caches
    if '--- LIBRARY CACHES' in content:
        section = content.split('--- LIBRARY CACHES')[1].split('---')[0]
        entries = parse_du_lines(section)
        if entries:
            report.append("## Top Caches (Safe to Clear)\n")
            report.append("| Cache | Size | Category |")
            report.append("|-------|------|----------|")
            total_cache = 0
            for size, path in entries:
                name = os.path.basename(path.rstrip('/'))
                total_cache += parse_size_to_bytes(size)
                report.append(f"| {name} | {size} | cache |")
            report.append(f"\n**Total cache size: {bytes_to_human(total_cache)}**\n")

    # Parse applications
    if '--- APPLICATIONS BY SIZE' in content:
        section = content.split('--- APPLICATIONS BY SIZE')[1].split('---')[0]
        entries = parse_du_lines(section)
        if entries:
            report.append("## Largest Applications\n")
            report.append("| Application | Size |")
            report.append("|-------------|------|")
            for size, path in entries:
                name = os.path.basename(path.rstrip('/'))
                report.append(f"| {name} | {size} |")
            report.append("")

    # TM exclusion status
    if '--- TIME MACHINE EXCLUSION STATUS ---' in content:
        section = content.split('--- TIME MACHINE EXCLUSION STATUS ---')[1].split('---')[0]
        included = []
        for line in section.strip().split('\n'):
            if '[Included]' in line:
                path = line.split(']')[1].strip()
                included.append(path)
        if included:
            report.append("## Time Machine: Paths That Should Be Excluded\n")
            report.append("These regenerable paths are currently being backed up unnecessarily:\n")
            for p in included:
                report.append(f"- `{p}`")
            report.append("\nRun these to exclude them:")
            report.append("```bash")
            for p in included:
                report.append(f'sudo tmutil addexclusion "{p}"')
            report.append("```\n")

    # Recommendations
    report.append("## Quick Cleanup Commands\n")
    report.append("### Tier 1: Safe Cache Cleanup")
    report.append("```bash")
    report.append("npm cache clean --force")
    report.append("yarn cache clean")
    report.append("pip cache purge")
    report.append("brew cleanup --prune=all")
    report.append("go clean -cache")
    report.append('rm -rf ~/Library/Caches/*.ShipIt')
    report.append("```\n")
    report.append("### Tier 2: Time Machine Optimization")
    report.append("```bash")
    report.append("# Thin local snapshots older than 1 day")
    report.append("sudo tmutil thinlocalsnapshots / 86400 1")
    report.append("```\n")

    with open(output_file, 'w') as f:
        f.write('\n'.join(report))

    print(f"Report saved to {output_file}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 generate_report.py <audit_file> <output_file>")
        sys.exit(1)
    generate_report(sys.argv[1], sys.argv[2])
