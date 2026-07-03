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


SECTION_HEADER_RE = re.compile(r'^---\s+(.+?)\s+---\s*$', re.MULTILINE)


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
        match = re.match(r'([\d.]+\s*[KMGTB])\s+(.+)$', line, re.IGNORECASE)
        if match:
            results.append((match.group(1), match.group(2)))
    return results


def normalize_section_name(name):
    """Drop count suffixes like '(TOP 20)' from audit section names."""
    return re.sub(r'\s+\([^)]*\)$', '', name.strip())


def iter_audit_sections(content):
    """Yield (section_name, section_body) for dashed audit sections."""
    matches = list(SECTION_HEADER_RE.finditer(content))
    for index, match in enumerate(matches):
        title = normalize_section_name(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        yield title, content[start:end]


def extract_section(content, name):
    """Extract text under a dashed audit section header."""
    for section_name, section_body in iter_audit_sections(content):
        if section_name == name:
            return section_body
    return ""


def categorize_path(path):
    """Categorize a path into a cleanup category."""
    path_lower = path.lower()
    path_parts = [part for part in path_lower.split('/') if part]
    if '/caches/' in path_lower or '/.cache' in path_lower or '_cacache' in path_lower:
        return 'cache'
    if any(x in path_lower for x in ['.npm', '.yarn', '.cargo', '.rustup', '.pyenv', 'homebrew', '/library/developer']):
        return 'dev-tools'
    if any(x in path_lower for x in ['google/drivefs', 'cloudstorage', 'dropbox', 'icloud', 'mobile documents']):
        return 'cloud-sync'
    if '/application support/' in path_lower:
        return 'app-data'
    if '/library/containers' in path_lower or path_lower.endswith('/library'):
        return 'app-data'
    if '.app' in path_lower or '/applications/' in path_lower or path_lower.endswith('/applications'):
        return 'app'
    if any(part in path_parts for part in ['downloads', 'documents', 'desktop', 'movies', 'music', 'pictures']):
        return 'user-data'
    return 'system'


def risk_for_category(category):
    """Return user-facing cleanup risk text for a finding category."""
    risks = {
        'cache': 'Low - regenerable',
        'dev-tools': 'Low/Medium - rebuild or re-download cost',
        'app': 'Judgment required',
        'app-data': 'Medium - may contain app state',
        'cloud-sync': 'High - cloud sync data',
        'user-data': 'High - user files',
        'system': 'Review required',
    }
    return risks.get(category, 'Review required')


def recommended_action_for(category, path):
    """Return a short action recommendation for a finding."""
    path_lower = path.lower()
    if category == 'cache':
        if '.shipit' in path_lower:
            return 'Clear only after closing the app and approving the command'
        return 'Clear after approval; apps may re-download or rebuild it'
    if category == 'dev-tools':
        return 'Use tool-specific cleanup after approval'
    if category == 'app':
        return 'Uninstall only if unused'
    if category == 'app-data':
        return 'Inspect before removing; may include settings or local data'
    if category == 'cloud-sync':
        return 'Review sync settings; do not delete blindly'
    if category == 'user-data':
        return 'Move or archive before deleting'
    return 'Review manually before changing'


def escape_markdown_cell(value):
    """Escape Markdown table cell delimiters."""
    return str(value).replace('|', r'\|')


def collect_findings(content):
    """Collect and rank du-style findings from every audit section."""
    findings_by_path = {}
    for section_name, section_body in iter_audit_sections(content):
        for size, path in parse_du_lines(section_body):
            num_bytes = parse_size_to_bytes(size)
            category = categorize_path(path)
            existing = findings_by_path.get(path)
            if existing and existing['bytes'] >= num_bytes:
                if section_name not in existing['sections']:
                    existing['sections'].append(section_name)
                continue
            findings_by_path[path] = {
                'size': size.strip(),
                'bytes': num_bytes,
                'path': path,
                'category': category,
                'risk': risk_for_category(category),
                'action': recommended_action_for(category, path),
                'sections': [section_name],
            }
    return sorted(findings_by_path.values(), key=lambda finding: finding['bytes'], reverse=True)


def collect_audit_coverage(content):
    """Collect missing, skipped, and unreadable audit checks."""
    coverage = []
    for section_name, section_body in iter_audit_sections(content):
        for raw_line in section_body.splitlines():
            line = raw_line.strip()
            match = re.match(r'^(MISSING|SKIPPED|UNREADABLE):\s*(.+)$', line)
            if match:
                coverage.append({
                    'section': section_name,
                    'status': match.group(1),
                    'detail': match.group(2),
                })
    return coverage


def add_command(commands, key, expected_bytes, command, why):
    """Add or merge a tailored cleanup command suggestion."""
    if key in commands:
        commands[key]['bytes'] += expected_bytes
        return
    commands[key] = {
        'bytes': expected_bytes,
        'command': command,
        'why': why,
    }


def build_tailored_commands(findings, snapshot_count):
    """Build cleanup command suggestions only from actual findings."""
    commands = {}
    for finding in findings:
        path = finding['path']
        path_lower = path.lower()
        size = finding['bytes']

        if path_lower.endswith('/.npm') or '/.npm/' in path_lower:
            add_command(
                commands, 'npm', size, 'npm cache clean --force',
                'npm cache data was found in the audit',
            )
        elif '/caches/pip' in path_lower or path_lower.endswith('/pip/cache'):
            add_command(
                commands, 'pip', size, 'pip cache purge',
                'pip cache data was found in the audit',
            )
        elif '/caches/ms-playwright' in path_lower:
            add_command(
                commands, 'playwright', size, f'rm -rf "{path}"',
                'Playwright browser cache was found in the audit',
            )
        elif '.shipit' in path_lower:
            add_command(
                commands, f'shipit:{path}', size, f'rm -rf "{path}"',
                'app update cache was found in the audit',
            )
        elif '/caches/homebrew' in path_lower:
            add_command(
                commands, 'homebrew', size, 'brew cleanup --prune=all',
                'Homebrew cache data was found in the audit',
            )
        elif '/caches/go-build' in path_lower:
            add_command(
                commands, 'go', size, 'go clean -cache',
                'Go build cache was found in the audit',
            )
        elif '/caches/pnpm' in path_lower or '.pnpm-store' in path_lower:
            add_command(
                commands, 'pnpm', size, 'pnpm store prune',
                'pnpm store/cache data was found in the audit',
            )
        elif '/.yarn' in path_lower or '/yarn/cache' in path_lower:
            add_command(
                commands, 'yarn', size, 'yarn cache clean',
                'Yarn cache data was found in the audit',
            )

    if snapshot_count and snapshot_count > 0:
        add_command(
            commands, 'tm-snapshots', 0, 'sudo tmutil thinlocalsnapshots / 86400 1',
            f'{snapshot_count} Time Machine local snapshots were found',
        )

    return list(commands.values())


def generate_report(audit_file, output_file):
    """Generate markdown report from audit data."""
    with open(audit_file, 'r') as f:
        content = f.read()

    findings = collect_findings(content)
    coverage = collect_audit_coverage(content)
    snapshot_count = 0

    report = []
    report.append(f"# Mac Disk Cleanup Report")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Parse disk overview
    section = extract_section(content, 'DISK OVERVIEW')
    if section:
        report.append("## Disk Overview")
        report.append("```")
        report.append(section.strip())
        report.append("```\n")

    # Parse snapshot count
    if 'Snapshot count:' in content:
        match = re.search(r'Snapshot count:\s*(\d+)', content)
        if match:
            snapshot_count = int(match.group(1))
            report.append(f"### Time Machine Local Snapshots: **{snapshot_count}**")
            if snapshot_count > 10:
                report.append(f"> ⚠️ {snapshot_count} local snapshots detected. These consume invisible disk space")
                report.append(f"> (typically 50-150 GB). Consider thinning with:")
                report.append(f"> `sudo tmutil thinlocalsnapshots / 86400 1`\n")

    if findings:
        report.append("## Top Findings\n")
        report.append("| Size | Path | Category | Risk | Recommended Action |")
        report.append("|------|------|----------|------|--------------------|")
        for finding in findings[:25]:
            report.append(
                "| {size} | `{path}` | {category} | {risk} | {action} |".format(
                    size=escape_markdown_cell(finding['size']),
                    path=escape_markdown_cell(finding['path']),
                    category=escape_markdown_cell(finding['category']),
                    risk=escape_markdown_cell(finding['risk']),
                    action=escape_markdown_cell(finding['action']),
                )
            )
        report.append("")

    # Parse user directories
    section = extract_section(content, 'USER DIRECTORIES')
    if section:
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
    section = extract_section(content, 'LIBRARY CACHES')
    if section:
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
    section = extract_section(content, 'APPLICATIONS BY SIZE')
    if section:
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
    section = extract_section(content, 'TIME MACHINE EXCLUSION STATUS')
    if section:
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

    if coverage:
        report.append("## Audit Coverage\n")
        report.append("These checks were not fully measured during the audit:\n")
        report.append("| Section | Status | Detail |")
        report.append("|---------|--------|--------|")
        for item in coverage:
            report.append(
                "| {section} | {status} | `{detail}` |".format(
                    section=escape_markdown_cell(item['section']),
                    status=escape_markdown_cell(item['status']),
                    detail=escape_markdown_cell(item['detail']),
                )
            )
        report.append("")

    # Recommendations
    report.append("## Quick Cleanup Commands\n")
    report.append("These commands are suggestions only. Review and approve any command before running it.\n")
    tailored_commands = build_tailored_commands(findings, snapshot_count)
    if tailored_commands:
        report.append("| Expected impact | Why shown | Command |")
        report.append("|-----------------|-----------|---------|")
        for command in tailored_commands:
            impact = bytes_to_human(command['bytes']) if command['bytes'] else 'Not directly measurable'
            report.append(
                "| {impact} | {why} | `{cmd}` |".format(
                    impact=escape_markdown_cell(impact),
                    why=escape_markdown_cell(command['why']),
                    cmd=escape_markdown_cell(command['command']),
                )
            )
        report.append("")
    else:
        report.append("No tailored cleanup commands were generated from the measured findings.\n")

    with open(output_file, 'w') as f:
        f.write('\n'.join(report))

    print(f"Report saved to {output_file}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 generate_report.py <audit_file> <output_file>")
        sys.exit(1)
    generate_report(sys.argv[1], sys.argv[2])
