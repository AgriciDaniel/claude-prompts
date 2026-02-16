---
name: prompt-enhance
description: >
  Enhance and improve existing AI prompts using professional techniques
  from a 2,500+ prompt database. Adds detail, fixes structure, optimizes
  for specific models, and applies proven patterns from top-performing prompts.
  Use when user says "enhance my prompt", "improve this prompt",
  "make this prompt better", "optimize prompt", "fix my prompt",
  or "upgrade this prompt".
---

# Prompt Enhancer

Take any existing prompt and supercharge it using techniques from 2,500+ curated prompts.

## Enhancement Workflow

### Step 1: Analyze the Input Prompt

Evaluate the user's prompt on these dimensions:
- **Specificity** (1-5): How detailed is the subject description?
- **Technical quality** (1-5): Camera, lighting, composition details?
- **Style clarity** (1-5): Is the aesthetic clearly defined?
- **Model optimization** (1-5): Uses model-specific syntax correctly?
- **Length appropriateness** (1-5): Right length for the target model?

Present a brief score card before enhancing.

### Step 2: Find Similar Top Prompts

Search for high-quality reference prompts:
```bash
python3 {PROMPT_ENGINE_DIR}/scripts/search_prompts.py "KEY_TERMS" --limit 5
```

### Step 3: Apply Enhancement Techniques

Choose from these enhancement strategies based on what's missing:

**Detail Injection** (for low specificity):
- Add material textures ("brushed aluminum", "weathered leather")
- Add environmental details ("dust particles in light", "morning dew")
- Add character details ("freckled skin", "calloused hands")

**Technical Elevation** (for missing camera/lighting):
- Add camera specs ("shot on Canon R5, 85mm f/1.2")
- Add lighting ("golden hour backlighting", "Rembrandt lighting")
- Add film stocks ("Kodak Portra 400 colors", "Fuji Velvia saturation")

**Style Anchoring** (for unclear aesthetic):
- Add photographer/artist references ("in the style of Annie Leibovitz")
- Add film/era references ("Y2K aesthetic", "1970s Kodachrome")
- Add mood keywords ("moody", "ethereal", "gritty")

**Negative Refinement** (for models that support it):
- Add negative prompts to exclude unwanted elements
- Specify what NOT to include ("no text", "no watermark")

**Structure Optimization** (for poor organization):
- Reorder elements: subject first, then environment, then style
- Group related modifiers together
- Remove redundant or conflicting terms

### Step 4: Present Enhanced Version

Output format:
1. **Original prompt** (for comparison)
2. **Enhanced prompt** (the improved version)
3. **What changed** (bullet list of specific improvements)
4. **Score improvement** (before -> after on 5-point scale)
5. **Variations** (2-3 alternative enhanced versions)

## Enhancement Rules

- Never remove the user's core intent/subject
- Preserve the user's preferred style if stated
- Keep enhancements relevant to the target model
- Don't over-engineer: some prompts are intentionally minimal
- Always explain WHY each change was made
