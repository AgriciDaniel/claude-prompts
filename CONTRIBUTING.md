# Contributing to Claude Prompts

Thanks for your interest in contributing! Here's how you can help.

## Reporting Bugs

- Use [GitHub Issues](https://github.com/AgriciDaniel/claude-prompts/issues) to report bugs
- Include: what you expected, what happened, steps to reproduce
- Include your Python version (`python3 --version`) and OS

## Suggesting Features

- Use [GitHub Discussions](https://github.com/AgriciDaniel/claude-prompts/discussions) to suggest features or share ideas
- Describe the use case and why it would be helpful

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test the search script: `python3 scripts/search_prompts.py --stats`
5. Test the install script: `bash install.sh`
6. Commit with a clear message describing the change
7. Push to your fork and open a Pull Request

## Adding Prompts

If you have prompt collections to contribute:

1. Add your Airtable shared view URLs to `scripts/scrape_airtable.py` (TABLES dict)
2. Run the scraper: `python3 scripts/scrape_airtable.py --output raw`
3. Run extraction: `python3 scripts/extract_prompts.py --input raw --output prompts`
4. Verify stats: `python3 scripts/search_prompts.py --stats`
5. Submit a PR with the updated `prompts/` directory

## Code Style

- Python: follow PEP 8, include docstrings for functions
- Markdown: use ATX headings (`#`), keep lines under 120 characters
- SKILL.md files: follow the [Agent Skills standard](https://agentskills.io) with YAML frontmatter
- Naming: kebab-case for directories, snake_case for Python files

## What Not to Commit

- Real Airtable URLs or API keys (keep in gitignored `raw/`)
- Personal data (emails, names, passwords)
- Large binary files or images
- The `raw/` directory (intermediate scraping data)
