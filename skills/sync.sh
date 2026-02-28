#!/usr/bin/env bash
# Sync personal skills into all agent skill directories.
# Run after adding a new skill directory.
#
# Sources from: life/skills/
# Targets: ~/.claude/skills, ~/.cursor/skills, ~/.codex/skills, ~/.gemini/skills, ~/clawd/skills

set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

AGENT_DIRS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.cursor/skills"
  "$HOME/.gemini/skills"
  "$HOME/clawd/skills"
)

linked=0
skipped=0
conflicts=0
removed=0

# Optional: --clean flag removes old symlinks pointing to dan-skills
CLEAN=false
if [[ "${1:-}" == "--clean" ]]; then
  CLEAN=true
  echo "Clean mode: removing old dan-skills symlinks..."
  for agent_dir in "${AGENT_DIRS[@]}"; do
    [[ -d "$agent_dir" ]] || continue
    for link in "$agent_dir"/*/; do
      link="${link%/}"
      [[ -L "$link" ]] || continue
      target="$(readlink "$link")"
      if [[ "$target" == *"dan-skills"* ]]; then
        rm "$link"
        echo "  removed old symlink: $link -> $target"
        ((removed++)) || true
      fi
    done
  done
  echo ""
fi

for skill_dir in "$SKILLS_DIR"/*/; do
  [[ -f "$skill_dir/SKILL.md" ]] || continue

  skill_name="$(basename "$skill_dir")"

  for agent_dir in "${AGENT_DIRS[@]}"; do
    mkdir -p "$agent_dir"
    link="$agent_dir/$skill_name"

    if [[ -L "$link" ]]; then
      existing_target="$(readlink "$link")"
      if [[ "$existing_target" == "$skill_dir" || "$existing_target" == "${skill_dir%/}" ]]; then
        ((skipped++)) || true
      else
        rm "$link"
        ln -s "$skill_dir" "$link"
        echo "  relinked: $skill_name -> $agent_dir (was: $existing_target)"
        ((linked++)) || true
      fi
    elif [[ -e "$link" ]]; then
      echo "  CONFLICT (not a symlink, skipping): $link"
      ((conflicts++)) || true
    else
      ln -s "$skill_dir" "$link"
      echo "  linked: $skill_name -> $agent_dir"
      ((linked++)) || true
    fi
  done
done

echo ""
echo "Done. $linked linked, $skipped already in place, $conflicts conflicts."
[[ "$CLEAN" == true ]] && echo "     $removed old dan-skills symlinks removed."
