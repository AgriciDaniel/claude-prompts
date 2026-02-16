---
name: prompt-build
description: >
  Build custom AI prompts from scratch using guided workflows and patterns
  from a 2,500+ prompt database. Supports image, video, and text prompts
  for Midjourney, Flux, Leonardo AI, DALL-E, Sora, and 12 more models.
  Use when user says "build a prompt", "create a prompt", "write a prompt",
  "make me a prompt", "new prompt", or "prompt from scratch".
---

# Prompt Builder

Build production-quality AI prompts using patterns extracted from 2,500+ curated prompts.

## Build Workflow

### Step 1: Determine Intent

Ask the user (if not already clear):
1. **Output type**: Image, Video, or Text?
2. **Target model**: Which AI model? (Midjourney, Flux, DALL-E, Leonardo, Sora, etc.)
3. **Subject**: What should the prompt create?
4. **Style/mood**: Any specific aesthetic?

### Step 2: Find Reference Prompts

Search the database for similar prompts to use as inspiration:
```bash
python3 {PROMPT_ENGINE_DIR}/scripts/search_prompts.py "SUBJECT" --model MODEL --limit 5
```

### Step 3: Construct the Prompt

Use this universal structure (adapt per model):

**Image Prompts:**
```
[Subject/Action] + [Setting/Environment] + [Lighting/Mood] + [Camera/Lens] +
[Style Reference] + [Technical Parameters]
```

**Video Prompts:**
```
[Camera Movement] + [Subject/Action] + [Setting] + [Lighting] +
[Duration/Speed] + [Style] + [Technical]
```

**Text Prompts:**
```
[Role/Context] + [Task] + [Constraints] + [Format] + [Tone] + [Examples]
```

### Step 4: Apply Model-Specific Syntax

Load `{PROMPT_ENGINE_DIR}/references/model-guide.md` for model-specific formatting rules:
- **Midjourney**: Use `--ar`, `--v`, `--style`, `--s`, `--chaos`
- **Flux**: Natural language, detailed descriptions work best
- **DALL-E**: Direct, descriptive, avoid negative prompts
- **Leonardo AI**: Use model-specific keywords (Phoenix, Alchemy)
- **Sora**: Camera movements, scene transitions, temporal descriptions

### Step 5: Review and Refine

Present the prompt with:
1. The full prompt text
2. Recommended parameters/settings
3. Similar prompts from the database for comparison
4. Suggested variations (3 alternatives)

## Quality Gates

- Prompt must be > 30 characters
- Must include subject + at least one modifier (style, lighting, or camera)
- Must use model-appropriate syntax
- No conflicting instructions (e.g., "realistic" + "cartoon")
