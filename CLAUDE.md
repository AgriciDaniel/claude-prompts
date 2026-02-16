# Claude Prompts -- AI Prompt Database and Builder

## Project Overview

This repository contains **Claude Prompts**, a Tier 4 Claude Code skill for searching,
building, enhancing, and adapting AI image/video prompts. It includes 2,500+ curated
prompts across 19 categories and 17 AI models. It follows the Agent Skills open standard
and the 3-layer architecture (directive, orchestration, execution).

## Architecture

```
claude-prompts/
  CLAUDE.md                          # This file (project instructions)
  prompt-engine/                     # Main orchestrator skill (Tier 4)
    SKILL.md                         # Entry point, routing table, database stats
    references/                      # Symlinked at install time
  skills/                            # Sub-skills
    prompt-build/SKILL.md           # Build custom prompts from scratch
    prompt-enhance/SKILL.md         # Enhance existing prompts with pro techniques
    prompt-adapt/SKILL.md           # Adapt prompts between AI models
    prompt-library/SKILL.md         # Browse, filter, and explore the library
  scripts/                           # Python execution scripts
    search_prompts.py               # Search and filter the prompt database
    extract_prompts.py              # Extract prompts from raw Airtable data
    scrape_airtable.py              # Scrape Airtable shared views (template)
  references/                        # Knowledge files
    model-guide.md                  # Model-specific syntax and best practices (17 models)
    prompt-patterns.md              # Common prompt engineering patterns
  prompts/                           # Prompt database (JSON)
    all_prompts.json                # Master file (2,503 prompts, ~5.4 MB)
    stats.json                      # Database statistics
    {category}/prompts.json         # Per-category files (19 categories)
  install.sh                         # Linux/macOS installation script
  install.ps1                        # Windows/PowerShell installation script
```

## Key Principles

1. **Progressive Disclosure**: Metadata always loaded, instructions on activation, references on demand
2. **Placeholder Paths**: Source files use `{PROMPT_ENGINE_DIR}` -- `install.sh` substitutes with actual repo path
3. **Symlinked References**: `references/` is symlinked into the installed skill to avoid duplication
4. **Template Scraper**: `scrape_airtable.py` ships with an empty TABLES dict -- users add their own URLs

## Development Rules

- Test search with `python3 scripts/search_prompts.py --stats` after changes
- Keep SKILL.md files under 500 lines / 5000 tokens
- Reference files should be focused and under 200 lines
- Scripts must have docstrings, CLI interface, and JSON output
- Follow kebab-case naming for all skill directories
- Never commit real Airtable URLs or API keys (only in gitignored `raw/`)

## Commands

| Command | Purpose |
|---------|---------|
| `/prompt [query]` | Search prompts by keyword, category, model, or style |
| `/prompt-build` | Build a custom prompt from scratch with guided workflow |
| `/prompt-enhance` | Enhance an existing prompt with pro techniques |
| `/prompt-adapt` | Adapt a prompt for a different AI model |
| `/prompt-library` | Browse, filter, and explore the full prompt library |

## Data Pipeline

1. **Scrape**: `scrape_airtable.py` extracts raw data from Airtable shared views (Playwright)
2. **Extract**: `extract_prompts.py` deduplicates, filters noise, categorizes, and infers models
3. **Output**: `prompts/all_prompts.json` (master) + per-category JSONs + `stats.json`
4. **Install**: `install.sh` copies skills to `~/.claude/skills/`, substitutes paths, symlinks references
