#!/usr/bin/env python3
"""Public-readiness regression checks for the FreeUp Space CLI.

These tests use the synthetic audit fixture only. They never run a live audit
and never execute cleanup commands.
"""

from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "freeup_space.py"
AUDIT_FIXTURE = ROOT / "tests" / "fixtures" / "sample_audit.txt"


def run_command(args, allow_failure=False):
    result = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0 and not allow_failure:
        print(f"Command failed: {' '.join(str(arg) for arg in args)}", file=sys.stderr)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
    return result


def require(text, phrase, label):
    if phrase not in text:
        print(f"{label} missing expected phrase: {phrase}", file=sys.stderr)
        print(f"\n{label} output:\n{text}", file=sys.stderr)
        return False
    return True


def reject(text, phrase, label):
    if phrase in text:
        print(f"{label} contains deprecated phrase: {phrase}", file=sys.stderr)
        print(f"\n{label} output:\n{text}", file=sys.stderr)
        return False
    return True


def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        report_path = tmp_path / "public-report.md"
        plan_report_path = tmp_path / "public-plan-report.md"

        help_result = run_command([sys.executable, str(CLI), "--help"])
        if help_result.returncode != 0:
            return help_result.returncode
        for phrase in ["--audit-output", "--report-output", "--no-open", "--non-interactive"]:
            if not require(help_result.stdout, phrase, "root help"):
                return 1

        report_result = run_command(
            [
                sys.executable,
                str(CLI),
                "report",
                "--input",
                str(AUDIT_FIXTURE),
                "--output",
                str(report_path),
            ]
        )
        if report_result.returncode != 0:
            return report_result.returncode
        report = report_path.read_text(encoding="utf-8")
        for phrase in [
            "macOS storage note",
            "APFS",
            "sealed system volume",
            "Lower-Risk Caches",
            "Command Suggestions: Review Before Running",
            "No command in this report has been run by FreeUp Space.",
        ]:
            if not require(report, phrase, "report"):
                return 1
        for phrase in ["Top Caches (Safe to Clear)", "## Quick Cleanup Commands"]:
            if not reject(report, phrase, "report"):
                return 1

        plan_result = run_command(
            [
                sys.executable,
                str(CLI),
                "plan",
                "--input",
                str(AUDIT_FIXTURE),
                "--output",
                str(plan_report_path),
            ]
        )
        if plan_result.returncode != 0:
            return plan_result.returncode
        for phrase in [
            "Manual action suggestions to review before running",
            "Command text (not executed):",
            "No cleanup commands were executed.",
        ]:
            if not require(plan_result.stdout, phrase, "plan"):
                return 1
        if not reject(plan_result.stdout, "Cleanup commands to review manually", "plan"):
            return 1
        if not plan_report_path.exists():
            print("plan --output did not generate report", file=sys.stderr)
            return 1

        missing_report = run_command(
            [
                sys.executable,
                str(CLI),
                "report",
                "--input",
                str(tmp_path / "missing-audit.txt"),
                "--output",
                str(tmp_path / "missing-report.md"),
            ],
            allow_failure=True,
        )
        if missing_report.returncode != 2:
            print(f"report missing-input exit was {missing_report.returncode}, expected 2", file=sys.stderr)
            return 1

        missing_plan = run_command(
            [sys.executable, str(CLI), "plan", "--input", str(tmp_path / "missing-audit.txt")],
            allow_failure=True,
        )
        if missing_plan.returncode != 2:
            print(f"plan missing-input exit was {missing_plan.returncode}, expected 2", file=sys.stderr)
            return 1

    print("Public readiness regression test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
