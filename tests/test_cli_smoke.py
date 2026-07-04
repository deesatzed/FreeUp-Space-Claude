#!/usr/bin/env python3
"""Smoke test for the FreeUp Space v0.2 CLI surface.

The test uses a synthetic audit fixture and a temporary HOME so it never runs a
live disk audit and never touches the user's real install location.
"""

from pathlib import Path
import os
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "freeup_space.py"
INSTALLER = ROOT / "install.sh"
UNINSTALLER = ROOT / "uninstall.sh"
AUDIT_FIXTURE = ROOT / "tests" / "fixtures" / "sample_audit.txt"


def run_command(args, env=None):
    result = subprocess.run(
        args,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(f"Command failed: {' '.join(str(arg) for arg in args)}", file=sys.stderr)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
    return result


def require_phrases(text, phrases, label):
    missing = [phrase for phrase in phrases if phrase not in text]
    if missing:
        print(f"{label} missing expected phrases:", file=sys.stderr)
        for phrase in missing:
            print(f"- {phrase}", file=sys.stderr)
        print(f"\n{label} output:\n{text}", file=sys.stderr)
        return False
    return True


def main():
    for path in [CLI, INSTALLER, UNINSTALLER, AUDIT_FIXTURE]:
        if not path.exists():
            print(f"Missing required file: {path}", file=sys.stderr)
            return 1

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        report_path = tmp_path / "fixture-report.md"

        help_result = run_command([sys.executable, str(CLI), "--help"])
        if help_result.returncode != 0:
            return help_result.returncode
        if not require_phrases(
            help_result.stdout,
            [
                "audit",
                "report",
                "doctor",
                "dev",
                "models",
                "plan",
                "--audit-output",
                "--report-output",
                "--no-open",
                "--non-interactive",
            ],
            "help",
        ):
            return 1

        doctor_result = run_command([sys.executable, str(CLI), "doctor"])
        if doctor_result.returncode != 0:
            return doctor_result.returncode
        if not require_phrases(
            doctor_result.stdout,
            ["Python 3", "Bash", "Desktop", "live audit"],
            "doctor",
        ):
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
        if not require_phrases(report, ["# Mac Disk Cleanup Report", "## Top Findings"], "report"):
            return 1

        plan_result = run_command(
            [sys.executable, str(CLI), "plan", "--input", str(AUDIT_FIXTURE)]
        )
        if plan_result.returncode != 0:
            return plan_result.returncode
        if not require_phrases(
            plan_result.stdout,
            [
                "review plan",
                "Manual action suggestions to review before running",
                "Command text (not executed)",
                "No cleanup commands were executed",
            ],
            "plan",
        ):
            return 1

        fake_home = tmp_path / "home"
        fake_home.mkdir()
        (fake_home / "Desktop").mkdir()
        install_env = os.environ.copy()
        install_env["HOME"] = str(fake_home)
        install_env["PATH"] = f"{fake_home / '.local' / 'bin'}{os.pathsep}{install_env.get('PATH', '')}"

        install_result = run_command(["bash", str(INSTALLER)], env=install_env)
        if install_result.returncode != 0:
            return install_result.returncode

        wrapper = fake_home / ".local" / "bin" / "freeup-space"
        if not wrapper.exists():
            print(f"Installer did not create wrapper: {wrapper}", file=sys.stderr)
            return 1

        wrapper_help = run_command(["freeup-space", "--help"], env=install_env)
        if wrapper_help.returncode != 0:
            return wrapper_help.returncode

        wrapper_report = tmp_path / "wrapper-report.md"
        wrapper_report_result = run_command(
            [
                "freeup-space",
                "report",
                "--input",
                str(AUDIT_FIXTURE),
                "--output",
                str(wrapper_report),
            ],
            env=install_env,
        )
        if wrapper_report_result.returncode != 0:
            return wrapper_report_result.returncode
        if not wrapper_report.exists():
            print("Installed wrapper did not generate report output", file=sys.stderr)
            return 1

        uninstall_result = run_command(["bash", str(UNINSTALLER)], env=install_env)
        if uninstall_result.returncode != 0:
            return uninstall_result.returncode
        if wrapper.exists():
            print(f"Uninstaller did not remove wrapper: {wrapper}", file=sys.stderr)
            return 1

    print("CLI smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
