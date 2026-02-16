#!/usr/bin/env bash
# Install prompt-engine skill and sub-skills
# Usage: bash install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"
COUNT="unknown"

echo "Installing prompt-engine skill ecosystem..."
echo "Source: $SCRIPT_DIR"
echo "Target: $SKILLS_DIR"
echo ""

# Create skills directory if needed
mkdir -p "$SKILLS_DIR"

# [1/6] Install main skill (with path substitution)
echo "[1/6] Installing prompt-engine (main skill)..."
rm -rf "$SKILLS_DIR/prompt-engine"
cp -r "$SCRIPT_DIR/prompt-engine" "$SKILLS_DIR/prompt-engine"
# Replace {PROMPT_ENGINE_DIR} placeholder with actual repo path
sed -i "s|{PROMPT_ENGINE_DIR}|$SCRIPT_DIR|g" "$SKILLS_DIR/prompt-engine/SKILL.md"

# [2/6] Install sub-skills (with path substitution)
echo "[2/6] Installing sub-skills..."
for skill in prompt-build prompt-enhance prompt-adapt prompt-library; do
    echo "  [+] $skill"
    rm -rf "$SKILLS_DIR/$skill"
    cp -r "$SCRIPT_DIR/skills/$skill" "$SKILLS_DIR/$skill"
    sed -i "s|{PROMPT_ENGINE_DIR}|$SCRIPT_DIR|g" "$SKILLS_DIR/$skill/SKILL.md"
done

# [3/6] Link references (symlink to avoid duplication)
echo "[3/6] Linking references..."
ln -sfn "$SCRIPT_DIR/references" "$SKILLS_DIR/prompt-engine/references"

# [4/6] Verify scripts are accessible
echo "[4/6] Verifying scripts..."
if python3 "$SCRIPT_DIR/scripts/search_prompts.py" --stats > /dev/null 2>&1; then
    echo "  Search script: OK"
else
    echo "  Search script: WARNING - stats check failed"
fi

# [5/6] Verify prompt database
echo "[5/6] Verifying prompt database..."
if [ -f "$SCRIPT_DIR/prompts/all_prompts.json" ]; then
    COUNT=$(python3 -c "import json; print(len(json.load(open('$SCRIPT_DIR/prompts/all_prompts.json'))))")
    echo "  Prompts loaded: $COUNT"
else
    echo "  WARNING: Prompt database not found at $SCRIPT_DIR/prompts/"
fi

# [6/6] Clean up old installations
echo "[6/6] Cleaning up..."
if [ -d "$SKILLS_DIR/claude-prompt" ]; then
    echo "  Removing old claude-prompt skill (renamed to prompt-engine)..."
    rm -rf "$SKILLS_DIR/claude-prompt"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Installed skills:"
echo "  /prompt          -- Search and find prompts"
echo "  /prompt-build    -- Build custom prompts"
echo "  /prompt-enhance  -- Enhance existing prompts"
echo "  /prompt-adapt    -- Adapt prompts across models"
echo "  /prompt-library  -- Browse the prompt library"
echo ""
echo "Database: $COUNT prompts across 19 categories and 17 models"
echo "Repo path: $SCRIPT_DIR"
