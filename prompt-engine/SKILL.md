---
name: prompt-engine
description: >
  Ultimate AI prompt database and builder with 2,500+ curated prompts across
  19 categories and 17 AI models (Midjourney, Flux, Leonardo AI, DALL-E, Sora,
  Imagen, Mystic, Stable Diffusion, Ideogram, Adobe Firefly, and more). Search,
  build, enhance, and adapt prompts for image generation, video creation, text,
  and meta-prompt generators.
  Use when user says "prompt", "find a prompt", "build a prompt",
  "enhance my prompt", "adapt this prompt", "prompt library",
  "image prompt", "video prompt", "midjourney prompt", "flux prompt",
  or any AI prompt engineering task.
  Do NOT use for terminal/CLI prompts, JavaScript prompt() dialogs,
  user input prompts, or bash prompt customization.
---

# Prompt Engine -- Ultimate AI Prompt Database and Builder

2,500+ curated prompts across 19 categories, 17 AI models, and 4 output types.

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/prompt [query]` | Search prompts by keyword, category, model, or style |
| `/prompt-build` | Build a custom prompt from scratch with guided workflow |
| `/prompt-enhance` | Enhance an existing prompt with pro techniques |
| `/prompt-adapt` | Adapt a prompt for a different AI model |
| `/prompt-library` | Browse, filter, and explore the full prompt library |

## Orchestration Logic

1. If user provides a **search query** or asks to **find/search** -> run search workflow below
2. If user wants to **create/build** a new prompt -> route to `/prompt-build`
3. If user has an **existing prompt** to improve -> route to `/prompt-enhance`
4. If user wants to **convert** between models -> route to `/prompt-adapt`
5. If user wants to **browse/explore** -> route to `/prompt-library`
6. If ambiguous, show the Quick Reference table and ask

## Search Workflow (Default /prompt)

When user provides a search query:

1. Run the search script:
   ```bash
   python3 {PROMPT_ENGINE_DIR}/scripts/search_prompts.py "QUERY" [--category CAT] [--model MODEL] [--type TYPE] [--limit N]
   ```

2. Present results as a numbered list with:
   - Prompt text (truncated to 200 chars for preview)
   - Category, model, output type
   - Tags/styles if available

3. Let user select a prompt to see full details, or refine their search

## Error Handling

- **0 search results**: Suggest broadening the query, trying different keywords, or removing filters. Offer to show available categories with `--categories`.
- **Script fails**: Verify Python 3.10+ is available (`python3 --version`). Check that the database exists at `{PROMPT_ENGINE_DIR}/prompts/all_prompts.json`.
- **Empty or short prompt input**: For `/prompt-enhance` and `/prompt-adapt`, ask the user to provide a longer prompt (minimum 30 characters).

## Database Stats

| Metric | Value |
|--------|-------|
| Total prompts | 2,503 |
| Categories | 19 |
| AI Models | 17 |
| Output types | Video (1,225), Image (1,049), Generator (115), Text (114) |
| Model coverage | 78% of prompts have model attribution |
| Sources | 11 Airtable databases |

## Categories

| Category | Count | Description |
|----------|-------|-------------|
| fashion-editorial | 473 | Fashion, editorial, magazine shoots |
| video-general | 287 | Video-specific prompts |
| general | 221 | Multi-purpose prompts |
| portraits-people | 198 | Faces, characters, headshots |
| landscapes-nature | 180 | Mountains, oceans, forests, sunsets |
| abstract-backgrounds | 171 | Gradients, patterns, wallpapers |
| sci-fi-futuristic | 135 | Cyberpunk, robots, space, neon |
| architecture | 129 | Buildings, interiors, cityscapes |
| logos-icons | 116 | Logo design, icon sets, branding |
| generators | 115 | Meta-prompts that create prompts |
| text | 114 | Copywriting, content, storytelling |
| animated-3d | 92 | Pixar, 3D renders, anime |
| vehicles | 82 | Cars, motorcycles, racing |
| superheroes | 58 | Marvel, DC, superhero art |
| fantasy | 56 | Dragons, magic, medieval, mythical |
| products | 42 | Product photography, packshots |
| animals | 18 | Wildlife, pets, creatures |
| food-drink | 11 | Food photography, recipes |
| print-merchandise | 5 | T-shirts, stickers, merch |

## Models

Top models: Midjourney (981), Leonardo AI (237), Freepik (172),
Mystic (166), Flux (137), Any Platform (97), DALL-E (42), Imagen (26),
Sora (24), ChatGPT (22).

## Data Paths

- Prompt database: `{PROMPT_ENGINE_DIR}/prompts/`
- Master file: `{PROMPT_ENGINE_DIR}/prompts/all_prompts.json`
- Per-category: `{PROMPT_ENGINE_DIR}/prompts/{category}/prompts.json`
- Stats: `{PROMPT_ENGINE_DIR}/prompts/stats.json`
- Search script: `{PROMPT_ENGINE_DIR}/scripts/search_prompts.py`

## Reference Files

- `references/prompt-patterns.md` -- Common prompt engineering patterns and structures
- `references/model-guide.md` -- Model-specific syntax, features, and best practices
