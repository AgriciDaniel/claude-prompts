#!/usr/bin/env bash
set -euo pipefail

main() {
    echo "Uninstalling claude-prompts..."

    # Remove main skill
    rm -rf "${HOME}/.claude/skills/prompt-engine"

    # Remove sub-skills
    for skill in prompt-adapt prompt-build prompt-enhance prompt-library; do
        rm -rf "${HOME}/.claude/skills/${skill}"
    done

    echo "claude-prompts uninstalled."
    echo "Restart Claude Code to complete removal."
}

main "$@"
