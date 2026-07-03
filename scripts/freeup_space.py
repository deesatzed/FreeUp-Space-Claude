#!/usr/bin/env python3
"""FreeUp Space v0.2 command line interface."""

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
DISK_AUDIT_SCRIPT = SCRIPTS_DIR / "disk_audit.sh"
REPORT_GENERATOR = SCRIPTS_DIR / "generate_report.py"
DEFAULT_AUDIT_NAME = "FreeUp-Space-Audit.txt"
DEFAULT_REPORT_NAME = "FreeUp-Space-Report.md"

sys.path.insert(0, str(SCRIPTS_DIR))
from generate_report import (  # noqa: E402
    build_tailored_commands,
    bytes_to_human,
    collect_findings,
)


MODE_NOTES = {
    "general": "General mode: read-only audit, Markdown report, and approval-only recommendations.",
    "developer": (
        "Developer mode: v0.2 uses the safe audit/report path. Deeper project "
        "and developer artifact classifiers are planned after v0.2."
    ),
    "models": (
        "Model review mode: v0.2 uses the safe audit/report path. Detailed "
        "local model inventory is future work, and no models are deleted."
    ),
}


QUESTIONS = [
    (
        "What are you trying to do?",
        [
            "Urgently free space",
            "Understand what is using space",
            "Clean developer artifacts",
            "Review local AI/model storage",
            "Prepare for backup or migration",
        ],
        2,
    ),
    (
        "How technical are you?",
        ["Plain-English only", "Comfortable with Terminal commands", "Developer/power user"],
        1,
    ),
    (
        "Do you have an external drive available for moving large files?",
        ["No", "Yes", "Not sure"],
        3,
    ),
    (
        "What mode should we use?",
        ["General", "Developer", "Vibe coder", "Local AI models"],
        1,
    ),
]


def display_path(path):
    """Return a compact user-facing path when possible."""
    try:
        return str(path.expanduser())
    except AttributeError:
        return str(path)


def default_output_dir():
    """Return the preferred output directory for normal runs."""
    desktop = Path.home() / "Desktop"
    if desktop.is_dir():
        return desktop
    return Path.cwd()


def timestamped_path(directory, filename):
    """Return filename in directory, adding a timestamp if it already exists."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    if not path.exists():
        return path
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    return path.with_name(f"{path.stem}-{timestamp}{path.suffix}")


def default_audit_path():
    return timestamped_path(default_output_dir(), DEFAULT_AUDIT_NAME)


def default_report_path():
    return timestamped_path(default_output_dir(), DEFAULT_REPORT_NAME)


def ensure_parent(path):
    path.parent.mkdir(parents=True, exist_ok=True)


def run_command(args):
    """Run a subprocess without shell expansion."""
    return subprocess.run(args, text=True)


def run_audit(output_path):
    output_path = Path(output_path).expanduser()
    ensure_parent(output_path)
    print("Running read-only audit.")
    print(f"Audit output: {output_path}")
    result = run_command(["bash", str(DISK_AUDIT_SCRIPT), str(output_path)])
    if result.returncode != 0:
        print("Audit command failed.", file=sys.stderr)
        return result.returncode
    print("Audit complete. No cleanup commands were executed.")
    return 0


def run_report(input_path, output_path):
    input_path = Path(input_path).expanduser()
    output_path = Path(output_path).expanduser()
    if not input_path.exists():
        print(f"Audit input not found: {input_path}", file=sys.stderr)
        return 2
    ensure_parent(output_path)
    result = run_command([sys.executable, str(REPORT_GENERATOR), str(input_path), str(output_path)])
    if result.returncode != 0:
        print("Report generation failed.", file=sys.stderr)
        return result.returncode
    print(f"Report output: {output_path}")
    print("No cleanup commands were executed.")
    return 0


def maybe_open_report(report_path, no_open=False):
    if no_open:
        return
    if platform.system() != "Darwin":
        print("Not opening report automatically because this is not macOS.")
        return
    if not shutil.which("open"):
        print("Not opening report automatically because the macOS 'open' tool was not found.")
        return
    subprocess.run(["open", str(report_path)], check=False)


def prompt_for_context(non_interactive=False):
    if non_interactive or not sys.stdin.isatty():
        print("Using safe default answers because stdin is not interactive.")
        return

    print("FreeUp Space will run a read-only audit and generate a report.")
    print("It will not delete, move, clear caches, thin snapshots, or run sudo.\n")
    for prompt, options, default_index in QUESTIONS:
        print(prompt)
        for index, option in enumerate(options, start=1):
            marker = " (default)" if index == default_index else ""
            print(f"{index}. {option}{marker}")
        answer = input("> ").strip()
        if not answer:
            answer = str(default_index)
        print(f"Selected: {answer}\n")


def run_audit_report_flow(mode, audit_output=None, report_output=None, no_open=False, non_interactive=False):
    print("FreeUp Space v0.2")
    print(MODE_NOTES[mode])
    prompt_for_context(non_interactive=non_interactive)

    audit_path = Path(audit_output).expanduser() if audit_output else default_audit_path()
    report_path = Path(report_output).expanduser() if report_output else default_report_path()

    audit_status = run_audit(audit_path)
    if audit_status != 0:
        return audit_status

    report_status = run_report(audit_path, report_path)
    if report_status != 0:
        return report_status

    maybe_open_report(report_path, no_open=no_open)
    print("\nNext step: review the Markdown report and approve any cleanup command manually.")
    print(f"Report: {report_path}")
    return 0


def extract_snapshot_count(content):
    match = re.search(r"Snapshot count:\s*(\d+)", content)
    if not match:
        return 0
    return int(match.group(1))


def run_plan(input_path, output_path=None):
    input_path = Path(input_path).expanduser()
    if not input_path.exists():
        print(f"Audit input not found: {input_path}", file=sys.stderr)
        return 2

    if output_path:
        status = run_report(input_path, Path(output_path).expanduser())
        if status != 0:
            return status

    content = input_path.read_text(encoding="utf-8")
    findings = collect_findings(content)
    commands = build_tailored_commands(findings, extract_snapshot_count(content))

    print("FreeUp Space recommendations")
    print("No cleanup commands were executed.")

    if findings:
        print("\nTop findings:")
        for finding in findings[:5]:
            print(f"- {finding['size']} {finding['path']}")
            print(f"  Risk: {finding['risk']}")
            print(f"  Recommendation: {finding['action']}")
    else:
        print("\nNo size-ranked findings were parsed from the audit input.")

    if commands:
        print("\nCleanup commands to review manually:")
        for command in commands[:5]:
            impact = bytes_to_human(command["bytes"]) if command["bytes"] else "Not directly measurable"
            print(f"- Expected impact: {impact}")
            print(f"  Why shown: {command['why']}")
            print(f"  Command text: {command['command']}")
    else:
        print("\nNo tailored cleanup command text was generated from this audit.")

    print("\nReview the full report before approving any action.")
    return 0


def check_item(name, ok, detail):
    status = "OK" if ok else "MISSING"
    print(f"{status}: {name} - {detail}")
    return ok


def run_doctor():
    print("FreeUp Space doctor")
    print(f"Platform: {platform.system() or 'unknown'}")

    required_ok = True
    required_ok &= check_item("Python 3", sys.version_info.major == 3, sys.version.split()[0])

    bash_path = shutil.which("bash")
    required_ok &= check_item("Bash", bool(bash_path), bash_path or "not found on PATH")

    required_ok &= check_item(
        "disk audit script",
        DISK_AUDIT_SCRIPT.exists(),
        str(DISK_AUDIT_SCRIPT),
    )
    required_ok &= check_item(
        "report generator",
        REPORT_GENERATOR.exists(),
        str(REPORT_GENERATOR),
    )

    desktop = Path.home() / "Desktop"
    check_item("Desktop", desktop.is_dir(), str(desktop))

    if platform.system() == "Darwin":
        print("macOS live audit tools:")
        for tool in ["diskutil", "tmutil", "du", "open"]:
            path = shutil.which(tool)
            check_item(tool, bool(path), path or "not found on PATH")
    else:
        print("Non-macOS environment detected: live audit requires macOS.")
        print("Report generation and fixture-based tests can still run here.")
        for tool in ["diskutil", "tmutil", "du", "open"]:
            path = shutil.which(tool)
            label = "available" if path else "unavailable"
            print(f"Optional macOS tool {tool}: {label}")

    print("Doctor complete. No cleanup commands were executed.")
    return 0 if required_ok else 1


def add_flow_options(parser):
    parser.add_argument("--audit-output", help="Path for the generated audit text file.")
    parser.add_argument("--report-output", help="Path for the generated Markdown report.")
    parser.add_argument("--no-open", action="store_true", help="Do not open the report automatically.")
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Use safe default answers instead of prompting.",
    )


def build_parser():
    parser = argparse.ArgumentParser(
        prog="freeup-space",
        description=(
            "Safety-first macOS storage audit and report tool. It never deletes, "
            "moves, clears caches, thins snapshots, or runs sudo."
        ),
    )
    subparsers = parser.add_subparsers(dest="command")

    audit_parser = subparsers.add_parser("audit", help="Run the read-only disk audit.")
    audit_parser.add_argument("--output", help="Audit output path. Defaults to Desktop.")

    report_parser = subparsers.add_parser("report", help="Generate a Markdown report from an audit file.")
    report_parser.add_argument("--input", required=True, help="Audit text file to read.")
    report_parser.add_argument("--output", help="Markdown report output path. Defaults to Desktop.")

    subparsers.add_parser("doctor", help="Check Python, Bash, script paths, Desktop, and macOS tools.")

    dev_parser = subparsers.add_parser("dev", help="Run safe audit/report flow with developer-mode context.")
    add_flow_options(dev_parser)

    models_parser = subparsers.add_parser("models", help="Run safe audit/report flow with model-review context.")
    add_flow_options(models_parser)

    plan_parser = subparsers.add_parser("plan", help="Print report recommendations without executing them.")
    plan_parser.add_argument("--input", required=True, help="Audit text file to read.")
    plan_parser.add_argument("--output", help="Optional Markdown report output path.")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        return run_audit_report_flow("general")
    if args.command == "audit":
        return run_audit(Path(args.output).expanduser() if args.output else default_audit_path())
    if args.command == "report":
        output = Path(args.output).expanduser() if args.output else default_report_path()
        return run_report(Path(args.input).expanduser(), output)
    if args.command == "doctor":
        return run_doctor()
    if args.command == "dev":
        return run_audit_report_flow(
            "developer",
            audit_output=args.audit_output,
            report_output=args.report_output,
            no_open=args.no_open,
            non_interactive=args.non_interactive,
        )
    if args.command == "models":
        return run_audit_report_flow(
            "models",
            audit_output=args.audit_output,
            report_output=args.report_output,
            no_open=args.no_open,
            non_interactive=args.non_interactive,
        )
    if args.command == "plan":
        return run_plan(args.input, output_path=args.output)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
