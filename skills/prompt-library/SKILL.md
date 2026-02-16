---
name: prompt-library
description: >
  Browse, filter, and explore a curated library of 2,500+ AI prompts
  organized by 19 categories, 17 models, and 4 output types. View stats,
  discover trending styles, and export prompt collections.
  Use when user says "prompt library", "browse prompts", "show categories",
  "list prompts", "prompt collection", "explore prompts",
  or "what prompts do we have".
---

# Prompt Library

Browse and explore 2,500+ curated prompts with rich filtering.

## Library Commands

### Browse by Category
Show available categories with counts:
```bash
python3 {PROMPT_ENGINE_DIR}/scripts/search_prompts.py --categories
```

Then load a specific category:
```bash
python3 {PROMPT_ENGINE_DIR}/scripts/search_prompts.py --category CATEGORY --limit 10
```

### Browse by Model
List prompts for a specific AI model:
```bash
python3 {PROMPT_ENGINE_DIR}/scripts/search_prompts.py --model "Midjourney" --limit 10
```

### Browse by Output Type
Filter by output type (image, video, text, generator):
```bash
python3 {PROMPT_ENGINE_DIR}/scripts/search_prompts.py --type video --limit 10
```

### Stats Overview
Show database statistics:
```bash
python3 {PROMPT_ENGINE_DIR}/scripts/search_prompts.py --stats
```

### Random Prompt
Get a random prompt for inspiration:
```bash
python3 {PROMPT_ENGINE_DIR}/scripts/search_prompts.py --random [--category CAT] [--model MODEL]
```

## Display Format

When showing prompts, use this format:

```
## [Category] -- [Model]

**Prompt:**
> [Full prompt text]

**Tags:** [tag1], [tag2], [tag3]
**Output:** [image/video/text]
**Source:** [original Airtable source]
```

When showing multiple prompts, use a numbered list with truncated previews
(first 150 chars) and let the user select one for full details.

## Data Locations

- Stats: `{PROMPT_ENGINE_DIR}/prompts/stats.json`
- All prompts: `{PROMPT_ENGINE_DIR}/prompts/all_prompts.json`
- By category: `{PROMPT_ENGINE_DIR}/prompts/{category}/prompts.json`
