# AI Model Prompt Guide

Quick reference for model-specific syntax and best practices.

## Midjourney (981 prompts in DB)

**Syntax:** Natural language + parameters after `--`
**Best for:** Artistic, editorial, fantasy, stylized imagery

| Parameter | Example | Purpose |
|-----------|---------|---------|
| `--ar` | `--ar 16:9` | Aspect ratio |
| `--v` | `--v 6.1` | Model version |
| `--style` | `--style raw` | Less stylized, more photographic |
| `--s` | `--s 250` | Stylization (0-1000) |
| `--chaos` | `--chaos 50` | Variation (0-100) |
| `--q` | `--q 2` | Quality (0.25, 0.5, 1, 2) |
| `--no` | `--no text` | Negative prompt |
| `--niji` | `--niji 6` | Anime/illustration mode |
| `::` | `cat::2 dog::1` | Multi-prompt weighting |

**Tips:**
- Front-load important elements
- Use specific art references ("in the style of...")
- Shorter prompts = more creative freedom
- `--style raw` for photorealistic results

## Flux (137 prompts in DB)

**Syntax:** Pure natural language, detailed descriptions
**Best for:** Photorealism, text rendering, complex compositions

**Tips:**
- Longer, more descriptive prompts work better
- No parameter syntax -- everything is in the description
- Excellent at rendering text in images
- Specify camera and lens for photorealistic shots
- Variants: Flux 1.1 Pro, Flux Realism, Flux Kontext

## Leonardo AI (237 prompts in DB)

**Syntax:** Natural language + model selection + Alchemy toggle
**Best for:** Photorealistic portraits, game art, concept art

**Key models:**
- **Phoenix** -- General purpose, high quality
- **Alchemy** -- Enhanced detail and coherence
- **DreamShaper** -- Artistic/dreamy style
- **Absolute Reality** -- Photorealism

**Tips:**
- Select the right sub-model for your use case
- Use negative prompts for cleaner results
- Alchemy mode significantly improves quality
- Good for consistent character generation

## Freepik (172 prompts in DB)

**Syntax:** Natural language + style/format selection in Freepik's AI Image Generator
**Best for:** Stock-style images, social media graphics, marketing assets, commercial use

**Tips:**
- All outputs are commercially licensed (Freepik subscription)
- Descriptive natural language prompts work best
- Select style presets (photo, digital art, painting, 3D) for targeted output
- Strong at lifestyle, business, and marketing imagery
- Supports aspect ratio and resolution selection in the UI
- Good for quick, polished assets that match stock photography standards

## DALL-E (42 prompts in DB)

**Syntax:** Direct, descriptive natural language
**Best for:** Quick concepts, illustrations, simple compositions

**Tips:**
- Clear, straightforward descriptions work best
- Avoid overly technical photography jargon
- No negative prompt support
- Great for quick ideation and variations
- Supports inpainting and outpainting

## Sora (24 prompts in DB)

**Syntax:** Scene descriptions with temporal language
**Best for:** Video generation, camera movements, transitions

**Tips:**
- Describe camera movements explicitly ("slowly pans left", "tracking shot")
- Include temporal progression ("the scene begins with... then transitions to...")
- Specify mood and atmosphere
- Reference film techniques ("dolly zoom", "crane shot")
- Keep scenes focused (one main action per prompt)

## Mystic (166 prompts in DB)

**Syntax:** Natural language, detailed scene descriptions
**Variants:** Mystic 2.5, Mystic 2.5 Fluid, Mystic 2.5 Flexible
**Best for:** Video generation, motion, dynamic scenes

**Tips:**
- Describe motion explicitly
- Use cinematic language
- Specify camera behavior
- Good for music video style content

## Imagen / Imagen 4 (26 prompts in DB)

**Syntax:** Natural language
**Best for:** Photorealistic images, text rendering

**Tips:**
- Google's model, strong at photorealism
- Good text-in-image capability
- Direct descriptions work well

## Stable Diffusion / SDXL (1 prompt in DB)

**Syntax:** Comma-separated keywords + negative prompts
**Best for:** Fine-tuned models, LoRA customization

**Tips:**
- Use keyword stacking ("masterpiece, best quality, highly detailed")
- Negative prompts are critical ("worst quality, blurry, deformed")
- Checkpoint/LoRA selection matters more than prompt
- CFG scale and steps affect output significantly

## Adobe Firefly (8 prompts in DB)

**Syntax:** Natural language with style presets
**Best for:** Social media graphics, quick edits, commercially safe images

**Tips:**
- All outputs are commercially licensed (trained on Adobe Stock)
- Select a style preset first, then add descriptive text
- Supports generative fill and expand
- Good for marketing materials and stock-style images

## Ideogram (8 prompts in DB)

**Syntax:** Natural language + optional style tags
**Best for:** Typography in images, logo concepts, stylized text

**Tips:**
- Best-in-class text rendering in images
- Use quotation marks around text you want rendered
- Style tags help guide aesthetic direction
- Good for social media graphics with text overlays

## Grok (9 prompts in DB)

**Syntax:** Natural language (via xAI)
**Best for:** Creative image generation, fewer content restrictions

**Tips:**
- Direct descriptions work well
- Fewer style limitations than other models
- Good for experimental or edgy creative concepts

## PicLumen (8 prompts in DB)

**Syntax:** Natural language + negative prompts
**Best for:** Free image generation, photorealistic portraits

**Tips:**
- Supports negative prompts for refinement
- Multiple model options (realistic, anime, artistic)
- Free tier available with decent quality

## Canva (9 prompts in DB)

**Syntax:** Simple natural language descriptions
**Best for:** Marketing materials, social media posts, presentations

**Tips:**
- Integrated into Canva's design workflow
- Best for quick, template-friendly generations
- Keep prompts simple and direct
- Strong at brand-consistent content

## ChatGPT / DALL-E 3 (22 prompts in DB)

**Syntax:** Conversational natural language
**Best for:** Iterative refinement through conversation, text rendering

**Tips:**
- ChatGPT rewrites your prompt before sending to DALL-E 3
- Conversational refinement ("make it more blue", "add a sunset")
- Good text rendering inherited from DALL-E 3
- Use system prompts for consistent style across generations

## RenderNet (1 prompt in DB)

**Syntax:** Natural language with character consistency tools
**Best for:** Consistent character generation, AI portraits, face-focused imagery

**Tips:**
- Specializes in face/character consistency across multiple generations
- Use FaceLock feature for maintaining the same face across images
- Good for creating AI influencer content and character-driven series

## Universal Best Practices

1. **Subject first**: Start with the main subject
2. **Be specific**: "golden retriever puppy" > "dog"
3. **Use reference anchors**: "shot on Canon R5, 85mm f/1.2"
4. **Layer modifiers**: subject + environment + lighting + style
5. **Test and iterate**: Start simple, add complexity
