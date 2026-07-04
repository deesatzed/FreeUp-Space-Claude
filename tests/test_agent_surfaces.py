#!/usr/bin/env python3
"""Fixture-only tests for Codex/Claude skill and command surfaces."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SURFACES = ROOT / "agent_surfaces"
INSTALLER = ROOT / "scripts" / "install_agent_surfaces.sh"

SKILLS = ["freeup-space", "mac-app-audit", "mac-tools-federation"]
COMMANDS = ["freeup-space.md", "audit-apps.md", "mac-tools-federation.md"]


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def assert_contains(path: Path, fragments: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for fragment in fragments:
        if fragment not in text:
            raise AssertionError(f"{path} missing expected text: {fragment!r}")


def main() -> int:
    for skill in SKILLS:
        path = SURFACES / "skills" / skill / "SKILL.md"
        if not path.exists():
            return fail(f"Missing skill: {path}")
        assert_contains(path, ["---", "name:", "description:"])

    assert_contains(
        SURFACES / "skills" / "freeup-space" / "SKILL.md",
        ["agent-managed skill surface", "deterministic helper scripts", "Never delete"],
    )
    assert_contains(
        SURFACES / "skills" / "mac-app-audit" / "SKILL.md",
        ["Claude Code/Codex manager", "do not pretend", "implementation root"],
    )
    assert_contains(
        SURFACES / "skills" / "mac-tools-federation" / "SKILL.md",
        ["file contract", "Routing Rules", "Do not build an umbrella"],
    )

    for command in COMMANDS:
        path = SURFACES / "commands" / command
        if not path.exists():
            return fail(f"Missing command: {path}")
        assert_contains(path, ["allowed-tools:", "description:", "Never"])

    with tempfile.TemporaryDirectory() as tmpdir:
        env = os.environ.copy()
        env["HOME"] = tmpdir
        result = subprocess.run(
            ["bash", str(INSTALLER)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            return result.returncode

        for base in [".codex/skills", ".agents/skills", ".claude/skills"]:
            for skill in SKILLS:
                installed = Path(tmpdir) / base / skill / "SKILL.md"
                if not installed.exists():
                    return fail(f"Installer missed skill: {installed}")

        for base in [".claude/commands/mac-tools", ".codex/prompts/mac-tools"]:
            for command in COMMANDS:
                installed = Path(tmpdir) / base / command
                if not installed.exists():
                    return fail(f"Installer missed command: {installed}")

    print("Agent surface test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
