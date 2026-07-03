#!/usr/bin/env python3
"""Cross-platform smoke test for the report generator.

This test uses a synthetic audit fixture so CI never needs to run macOS disk tools
and never executes cleanup commands.
"""

from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
AUDIT_FIXTURE = ROOT / "tests" / "fixtures" / "sample_audit.txt"
REPORT_GENERATOR = ROOT / "scripts" / "generate_report.py"


def main() -> int:
    if not AUDIT_FIXTURE.exists():
        print(f"Missing fixture: {AUDIT_FIXTURE}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "disk-report.md"
        result = subprocess.run(
            [sys.executable, str(REPORT_GENERATOR), str(AUDIT_FIXTURE), str(output_path)],
            text=True,
            capture_output=True,
        )

        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            return result.returncode

        report = output_path.read_text(encoding="utf-8")
        required_phrases = [
            "# Mac Disk Cleanup Report",
            "## Disk Overview",
            "Time Machine Local Snapshots",
            "## Top Findings",
            "| Size | Path | Category | Risk | Recommended Action |",
            "/Users/test/Library",
            "/Users/test/Library/Application Support/Google/DriveFS",
            "## Audit Coverage",
            "MISSING",
            "SKIPPED",
            "## Directory Sizes",
            "## Top Caches",
            "## Largest Applications",
            "## Quick Cleanup Commands",
            "npm cache clean --force",
            "Expected impact",
        ]

        missing = [phrase for phrase in required_phrases if phrase not in report]
        if missing:
            print("Report missing expected phrases:", file=sys.stderr)
            for phrase in missing:
                print(f"- {phrase}", file=sys.stderr)
            print("\nGenerated report:\n", file=sys.stderr)
            print(report, file=sys.stderr)
            return 1

        unexpected_phrases = [
            "yarn cache clean",
            "brew cleanup --prune=all",
            "go clean -cache",
        ]
        unexpected = [phrase for phrase in unexpected_phrases if phrase in report]
        if unexpected:
            print("Report included non-findings-driven commands:", file=sys.stderr)
            for phrase in unexpected:
                print(f"- {phrase}", file=sys.stderr)
            print("\nGenerated report:\n", file=sys.stderr)
            print(report, file=sys.stderr)
            return 1

    print("Smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
