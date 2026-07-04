#!/usr/bin/env bash
set -euo pipefail

# Installs agent-native skill/command surfaces only.
# No audit, cleanup, package install, sudo, or ledger write is performed.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SURFACES_DIR="$REPO_ROOT/agent_surfaces"

install_skill() {
  src_dir="$1"
  dest_base="$2"
  name="$(basename "$src_dir")"
  dest_dir="$dest_base/$name"
  mkdir -p "$dest_dir"
  cp "$src_dir/SKILL.md" "$dest_dir/SKILL.md"
  printf 'Installed skill: %s\n' "$dest_dir"
}

install_command() {
  src_file="$1"
  dest_base="$2"
  mkdir -p "$dest_base"
  cp "$src_file" "$dest_base/$(basename "$src_file")"
  printf 'Installed command: %s\n' "$dest_base/$(basename "$src_file")"
}

if [ ! -d "$SURFACES_DIR/skills" ] || [ ! -d "$SURFACES_DIR/commands" ]; then
  printf 'ERROR: agent surfaces not found under %s\n' "$SURFACES_DIR" >&2
  exit 1
fi

CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
AGENTS_SKILLS_DIR="${AGENTS_SKILLS_DIR:-$HOME/.agents/skills}"
CLAUDE_SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
CLAUDE_COMMANDS_DIR="${CLAUDE_COMMANDS_DIR:-$HOME/.claude/commands/mac-tools}"
CODEX_PROMPTS_DIR="${CODEX_PROMPTS_DIR:-$HOME/.codex/prompts/mac-tools}"

for skill_dir in "$SURFACES_DIR"/skills/*; do
  [ -d "$skill_dir" ] || continue
  install_skill "$skill_dir" "$CODEX_SKILLS_DIR"
  install_skill "$skill_dir" "$AGENTS_SKILLS_DIR"
  install_skill "$skill_dir" "$CLAUDE_SKILLS_DIR"
done

for command_file in "$SURFACES_DIR"/commands/*.md; do
  [ -f "$command_file" ] || continue
  install_command "$command_file" "$CLAUDE_COMMANDS_DIR"
  install_command "$command_file" "$CODEX_PROMPTS_DIR"
done

printf 'Agent surfaces installed. No cleanup commands were executed.\n'
printf 'Start a new Codex or Claude Code session, or reload the client, if the current session does not show newly installed skills or commands.\n'
