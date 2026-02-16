# Changelog

All notable changes to this project will be documented in this file.

## v1.0.0 — Initial Release

### Added

- **2,503 curated prompts** extracted from 11 Airtable shared view sources
- **19 categories**: fashion-editorial, video-general, general, portraits-people, landscapes-nature, abstract-backgrounds, sci-fi-futuristic, architecture, logos-icons, generators, text, animated-3d, vehicles, superheroes, fantasy, products, animals, food-drink, print-merchandise
- **17 AI models**: Midjourney, Leonardo AI, Freepik, Mystic, Flux, DALL-E, Imagen, Sora, ChatGPT, Grok, Canva, PicLumen, Adobe Firefly, Ideogram, Stable Diffusion, RenderNet, Any Platform
- **4 output types**: Video (1,225), Image (1,049), Generator (115), Text (114)
- **5 skill commands**: `/prompt` (search), `/prompt-build`, `/prompt-enhance`, `/prompt-adapt`, `/prompt-library`
- Search script with full-text search, category/model/type filters, random prompt, and stats
- Airtable shared view scraper template for adding custom prompt sources
- Extraction pipeline with dedup, quality filtering, and auto-categorization
- Model-specific prompt guide covering all 17 models
- Prompt engineering patterns reference (cinematic, editorial, product, fantasy, video)
- Install script with path substitution, symlinks, and verification
