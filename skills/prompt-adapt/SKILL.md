---
name: prompt-adapt
description: >
  Adapt and convert AI prompts between different models and platforms.
  Translates between Midjourney, Flux, Leonardo AI, DALL-E, Sora, Imagen,
  Stable Diffusion, Adobe Firefly, Ideogram, and more. Handles syntax
  differences, parameter mapping, and model-specific optimizations.
  Use when user says "adapt prompt", "convert prompt", "translate prompt",
  "port to flux", "midjourney to dall-e", or "change model".
---

# Prompt Adapter

Convert prompts between AI models while preserving intent and maximizing output quality.

## Adaptation Workflow

### Step 1: Identify Source and Target

Determine:
1. **Source model**: What model was this prompt written for?
2. **Target model**: What model should it run on?
3. **Priority**: Preserve style fidelity or optimize for target strengths?

### Step 2: Analyze Source Prompt

Break down the prompt into components:
- Core subject/action
- Style modifiers
- Technical parameters (model-specific)
- Negative prompts (if any)
- Aspect ratio / dimensions

### Step 3: Apply Model Translation Rules

Load `{PROMPT_ENGINE_DIR}/references/model-guide.md` for detailed rules. Key translations:

**Midjourney -> Flux:**
- Remove `--ar`, `--v`, `--style`, `--s`, `--chaos` parameters
- Expand shorthand into natural language descriptions
- Flux prefers longer, more descriptive prompts
- Remove `::` weight syntax, integrate naturally

**Midjourney -> DALL-E:**
- Remove all `--` parameters
- Rewrite as clear, direct descriptions
- DALL-E prefers straightforward language over artistic jargon
- Remove negative prompts (DALL-E doesn't support them well)

**Flux -> Midjourney:**
- Add `--ar` for aspect ratio
- Add `--v 6.1` or appropriate version
- Condense long descriptions into key phrases
- Add style parameters (`--style raw` for photorealistic)

**Any -> Sora (Video):**
- Add camera movement descriptions (pan, zoom, tracking, etc.)
- Add temporal flow ("the scene transitions from... to...")
- Specify duration if possible
- Focus on motion and action over static details

**Any -> Leonardo AI:**
- Reference specific Leonardo models (Phoenix, Alchemy, etc.)
- Use Leonardo-specific quality tokens
- Adapt negative prompts to Leonardo format

### Step 4: Search for Target Model Examples

Find reference prompts in the target model:
```bash
python3 {PROMPT_ENGINE_DIR}/scripts/search_prompts.py "SUBJECT" --model TARGET_MODEL --limit 3
```

Use these as style references for the adaptation.

### Step 5: Present Adaptation

Output format:
1. **Original prompt** (source model labeled)
2. **Adapted prompt** (target model labeled)
3. **Translation notes** (what changed and why)
4. **Parameter mapping** (source params -> target params)
5. **Confidence level** (High/Medium/Low -- based on model compatibility)

## Common Pitfalls

- Midjourney weight syntax (`::2`) has no direct equivalent in most models
- DALL-E ignores most style parameters -- weave them into descriptions
- Sora needs temporal language that image models don't use
- Aspect ratios must be specified differently per platform
- Some styles only work well on specific models (e.g., `--niji` is Midjourney-only)
