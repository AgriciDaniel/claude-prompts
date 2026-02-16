#!/usr/bin/env python3
"""
Airtable Prompt Extractor
Processes raw scraped Airtable data into structured prompt records.
Handles both API data (preferred) and raw text fallback.

Usage: python extract_prompts.py --input raw/ --output prompts/
"""

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from collections import defaultdict


def build_column_map(schema: dict) -> dict:
    """Map column IDs to human-readable names."""
    col_map = {}
    for col in schema.get("columns", []):
        col_id = col.get("id", "")
        col_name = col.get("name", "")
        col_type = col.get("type", "")
        col_map[col_id] = {
            "name": col_name,
            "type": col_type,
            "typeOptions": col.get("typeOptions", {}),
        }
    return col_map


def build_select_map(schema: dict) -> dict:
    """Map select option IDs to their display names."""
    select_map = {}
    for col in schema.get("columns", []):
        col_type = col.get("type", "")
        if col_type in ("select", "multiSelect"):
            options = col.get("typeOptions", {}).get("choices", {})
            if isinstance(options, dict):
                for opt_id, opt_data in options.items():
                    if isinstance(opt_data, dict):
                        select_map[opt_id] = opt_data.get("name", opt_id)
                    else:
                        select_map[opt_id] = str(opt_data)
            elif isinstance(options, list):
                for opt in options:
                    if isinstance(opt, dict):
                        select_map[opt.get("id", "")] = opt.get("name", "")
    return select_map


def extract_rich_text(field_value) -> str:
    """Extract plain text from Airtable rich text field."""
    if isinstance(field_value, str):
        return field_value.strip()
    if isinstance(field_value, dict):
        doc_value = field_value.get("documentValue", [])
        if isinstance(doc_value, list):
            parts = []
            for segment in doc_value:
                if isinstance(segment, dict):
                    text = segment.get("insert", "")
                    if isinstance(text, str):
                        parts.append(text)
            return "".join(parts).strip()
    return ""


def extract_cell_value(field_value, col_info: dict, select_map: dict) -> str | list | bool | None:
    """Extract a clean value from a cell based on its column type."""
    col_type = col_info.get("type", "")

    if field_value is None:
        return None

    if col_type == "richText":
        return extract_rich_text(field_value)

    if col_type == "text":
        return str(field_value).strip() if field_value else None

    if col_type == "select":
        if isinstance(field_value, str):
            return select_map.get(field_value, field_value)
        return str(field_value)

    if col_type == "multiSelect":
        if isinstance(field_value, list):
            return [select_map.get(v, v) if isinstance(v, str) else str(v) for v in field_value]
        if isinstance(field_value, str):
            return [select_map.get(field_value, field_value)]
        return [str(field_value)]

    if col_type == "checkbox":
        return bool(field_value)

    if col_type == "multipleAttachment":
        if isinstance(field_value, list):
            attachments = []
            for att in field_value:
                if isinstance(att, dict):
                    attachments.append({
                        "id": att.get("id", ""),
                        "url": att.get("url", ""),
                        "filename": att.get("filename", ""),
                        "type": att.get("type", ""),
                        "size": att.get("size", 0),
                    })
            return attachments
        return []

    if col_type in ("number", "count", "autoNumber"):
        return field_value

    if col_type == "formula":
        if isinstance(field_value, dict):
            return field_value.get("value", str(field_value))
        return field_value

    if col_type == "url":
        return str(field_value).strip() if field_value else None

    # Fallback
    if isinstance(field_value, (str, int, float, bool)):
        return field_value
    if isinstance(field_value, dict):
        # Try to extract text from various structures
        for key in ("value", "text", "name", "label"):
            if key in field_value:
                return field_value[key]
        return str(field_value)
    if isinstance(field_value, list):
        return [str(v) for v in field_value]
    return str(field_value)


def extract_rows_from_table_data(tbl_id: str, tbl_data, col_map: dict, select_map: dict) -> list[dict]:
    """Extract rows from a single table data structure."""
    records = []
    rows = {}

    if isinstance(tbl_data, dict):
        # Format 1: partialRowById (readForSharedPages)
        rows = tbl_data.get("partialRowById", {})
        # Format 2: rowsById
        if not rows:
            rows = tbl_data.get("rowsById", {})
        # Format 3: rows list (read endpoint)
        if not rows:
            row_list = tbl_data.get("rows", [])
            if isinstance(row_list, list):
                rows = {r.get("id", f"row{i}"): r for i, r in enumerate(row_list) if isinstance(r, dict)}

    for row_id, row_data in rows.items():
        if not isinstance(row_data, dict):
            continue

        cell_values = row_data.get("cellValuesByColumnId", {})
        if not cell_values:
            cell_values = row_data.get("cells", {})
        if not cell_values:
            continue

        record = {
            "_id": row_id,
            "_table_id": tbl_id,
        }

        for col_id, cell_value in cell_values.items():
            col_info = col_map.get(col_id, {"name": col_id, "type": "unknown"})
            col_name = col_info["name"]
            clean_value = extract_cell_value(cell_value, col_info, select_map)
            if clean_value is not None:
                record[col_name] = clean_value

        # Only keep records that have meaningful content
        has_prompt = any(
            isinstance(v, str) and len(v) > 20
            for k, v in record.items()
            if k not in ("_id", "_table_id", "Name", "Date")
        )
        if has_prompt:
            records.append(record)

    return records


def extract_from_api(raw_data: dict) -> list[dict]:
    """Extract structured prompt records from API response data."""
    prompts = []
    api_data = raw_data.get("api_data")
    if not api_data:
        return prompts

    for api_resp in api_data:
        resp_url = api_resp.get("url", "")
        resp_data = api_resp.get("data", {}).get("data", {})
        if not resp_data:
            resp_data = api_resp.get("data", {})
        if not isinstance(resp_data, dict):
            continue

        # Skip attachment URL responses (check path only, not query params)
        from urllib.parse import urlparse as _urlparse
        url_path = _urlparse(resp_url).path
        if "readSignedAttachmentUrls" in url_path:
            continue

        # Get table schemas
        schemas = resp_data.get("tableSchemas", [])
        col_map = {}
        select_map = {}
        for schema in schemas:
            col_map.update(build_column_map(schema))
            select_map.update(build_select_map(schema))

        # Source 1: preloadPageQueryResults.tableDataById (readForSharedPages)
        preload_data = resp_data.get("preloadPageQueryResults", {}).get("tableDataById", {})
        if isinstance(preload_data, dict):
            for tbl_id, tbl_data in preload_data.items():
                records = extract_rows_from_table_data(tbl_id, tbl_data, col_map, select_map)
                prompts.extend(records)

        # Source 2: tableDatas (read endpoint) -- can be list or dict
        table_datas = resp_data.get("tableDatas", [])
        if isinstance(table_datas, list):
            for td in table_datas:
                if isinstance(td, dict):
                    tbl_id = td.get("id", "unknown")
                    records = extract_rows_from_table_data(tbl_id, td, col_map, select_map)
                    prompts.extend(records)
        elif isinstance(table_datas, dict):
            for tbl_id, tbl_data in table_datas.items():
                records = extract_rows_from_table_data(tbl_id, tbl_data, col_map, select_map)
                prompts.extend(records)

    return prompts


def extract_from_scroll(raw_data: dict) -> list[dict]:
    """Extract prompt records from scroll-collected text (fallback)."""
    prompts = []
    scroll_data = raw_data.get("scroll_data", {})
    texts = scroll_data.get("texts", [])
    images = scroll_data.get("images", [])

    if not texts:
        return prompts

    # Filter out noise (UI elements, buttons, etc.)
    noise_patterns = [
        r"^Report abuse$", r"^Log in$", r"^Sign up", r"^Add record$",
        r"^Filter$", r"^Sort$", r"^Category$", r"^Tags/Styles$",
        r"^Click each prompt", r"^Interface:", r"^Gallery$",
        r"^\d+$",  # bare numbers
    ]
    noise_re = re.compile("|".join(noise_patterns), re.IGNORECASE)

    # Known AI model names (categories)
    model_names = {
        "flux", "flux 1.1 pro", "flux realism", "flux kontext", "flux pro",
        "imagen 4", "imagen", "mystic 2.5 fluid", "mystic 2.5 flexible",
        "midjourney", "dall-e", "stable diffusion", "sdxl", "sd 3.5",
        "leonardo", "ideogram", "gpt-4", "claude", "gemini",
    }

    clean_texts = []
    for t in texts:
        if noise_re.match(t):
            continue
        if len(t) < 3:
            continue
        clean_texts.append(t)

    # Try to identify prompts (longer text items)
    for text in clean_texts:
        if len(text) > 50:
            # Likely a prompt
            prompt_record = {
                "_source": "scroll_text",
                "Prompt": text,
            }

            # Try to identify the model from nearby short texts
            # (this is a heuristic since we don't have structured data)
            prompts.append(prompt_record)

    # Add image URLs
    if images:
        for i, img_url in enumerate(images):
            if i < len(prompts):
                prompts[i]["_image_url"] = img_url

    return prompts


def compute_prompt_hash(prompt_text: str) -> str:
    """Compute a normalized hash for deduplication."""
    # Normalize: lowercase, strip whitespace, remove punctuation variations
    normalized = prompt_text.lower().strip()
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"[^\w\s]", "", normalized)
    return hashlib.md5(normalized.encode()).hexdigest()[:12]


def deduplicate_prompts(all_prompts: list[dict]) -> tuple[list[dict], int]:
    """Remove duplicate prompts based on text similarity."""
    seen_hashes = {}
    unique = []
    dupes = 0

    for prompt in all_prompts:
        # Find the main text field
        text = ""
        for key in ("Prompt", "prompt", "Full Prompt", "\U0001f916Full Prompt",
                    "Extract Prompt", "Description", "description",
                    "Prompt Example", "\U0001f4ddQuick Description", "Text", "text"):
            if key in prompt and isinstance(prompt[key], str):
                text = prompt[key]
                break

        if not text:
            # Check all string fields for the longest one
            longest = ""
            for v in prompt.values():
                if isinstance(v, str) and len(v) > len(longest):
                    longest = v
            text = longest

        if not text or len(text) < 20:
            continue

        h = compute_prompt_hash(text)
        if h in seen_hashes:
            dupes += 1
            # Merge any additional data into the existing record
            existing = seen_hashes[h]
            for k, v in prompt.items():
                if k not in existing or existing[k] is None:
                    existing[k] = v
            # Track source tables
            existing.setdefault("_sources", [])
            if prompt.get("_source_table"):
                existing["_sources"].append(prompt["_source_table"])
        else:
            prompt.setdefault("_sources", [])
            if prompt.get("_source_table"):
                prompt["_sources"].append(prompt["_source_table"])
            seen_hashes[h] = prompt
            unique.append(prompt)

    return unique, dupes


PROMPT_TEXT_FIELDS = (
    "Prompt", "prompt", "Full Prompt", "\U0001f916Full Prompt",
    "Extract Prompt", "Description", "description",
    "Prompt Example", "\U0001f4ddQuick Description", "Text", "text",
)

NOISE_PHRASES = [
    "coming soon", "new page", "placeholder", "lorem ipsum",
    "test", "untitled", "example",
]


def get_best_text(prompt: dict) -> str:
    """Find the best prompt text field from a record."""
    for key in PROMPT_TEXT_FIELDS:
        if key in prompt and isinstance(prompt[key], str) and len(prompt[key]) > 10:
            return prompt[key]
    # Fallback: longest string field
    longest = ""
    for k, v in prompt.items():
        if isinstance(v, str) and len(v) > len(longest) and not k.startswith("_"):
            longest = v
    return longest


def filter_noise(prompts: list[dict]) -> tuple[list[dict], int]:
    """Remove placeholder, empty, and noise prompts."""
    clean = []
    removed = 0
    for prompt in prompts:
        text = get_best_text(prompt)
        # Remove if no meaningful text
        if len(text) < 30:
            removed += 1
            continue
        # Remove placeholder entries
        text_lower = text.lower().strip()
        if any(text_lower == phrase or text_lower.startswith(phrase + "...") for phrase in NOISE_PHRASES):
            removed += 1
            continue
        clean.append(prompt)
    return clean, removed


KNOWN_MODELS = {
    "midjourney": "Midjourney",
    "leonardo ai": "Leonardo AI",
    "dall-e": "DALL-E",
    "dalle": "DALL-E",
    "stable diffusion": "Stable Diffusion",
    "flux": "Flux",
    "flux 1.1 pro": "Flux",
    "flux realism": "Flux",
    "flux kontext": "Flux",
    "flux pro": "Flux",
    "imagen": "Imagen",
    "imagen 4": "Imagen",
    "imagen3": "Imagen",
    "mystic": "Mystic",
    "mystic 2.5": "Mystic",
    "mystic 2.5 fluid": "Mystic",
    "mystic 2.5 flexible": "Mystic",
    "sora": "Sora",
    "ideogram": "Ideogram",
    "adobe firefly": "Adobe Firefly",
    "chatgpt": "ChatGPT",
    "grok": "Grok",
    "freepik": "Freepik",
    "piclumen": "PicLumen",
    "rendernet": "RenderNet",
    "canva": "Canva",
    "any platform": "Any Platform",
}


def parse_type_field(type_value: str) -> dict:
    """Parse the compound Type field into model, styles, and subject tags."""
    result = {"model": None, "styles": [], "subjects": []}
    if not type_value:
        return result

    # Split on 🎨 emoji if present
    if "🎨" in type_value:
        parts = type_value.split("🎨", 1)
        model_part = parts[0].strip().rstrip(" ")
        tags_part = parts[1].strip() if len(parts) > 1 else ""
    else:
        model_part = type_value.strip()
        tags_part = ""

    # Identify model
    model_lower = model_part.lower().strip()
    for key, name in KNOWN_MODELS.items():
        if key in model_lower:
            result["model"] = name
            break

    # Parse tags
    if tags_part:
        tags = [t.strip() for t in tags_part.split(",") if t.strip()]
        for tag in tags:
            result["styles"].append(tag)

    return result


def categorize_prompt(prompt: dict) -> tuple[str, dict]:
    """Determine category and extract metadata from a prompt.

    Returns (category, metadata_dict) where metadata includes model, styles, etc.
    """
    metadata = {"model": None, "styles": [], "output_type": "image"}

    # Parse Type field for model and style info
    type_val = ""
    for key in ("Type", "Category", "type", "category",
                "\U0001f4f1Type", "\U0001f680Type", "\U0001f37fCategory"):
        if key in prompt and prompt[key]:
            val = prompt[key]
            if isinstance(val, list):
                val = val[0] if val else ""
            type_val = str(val).strip()
            break

    if type_val:
        parsed = parse_type_field(type_val)
        metadata["model"] = parsed["model"]
        metadata["styles"] = parsed["styles"]

    # If no model found yet, check the dedicated "App" field (ai-influencer source)
    if not metadata["model"]:
        app_val = prompt.get("App", "")
        if isinstance(app_val, str) and app_val.strip():
            app_lower = app_val.strip().lower()
            for key, name in KNOWN_MODELS.items():
                if key in app_lower:
                    metadata["model"] = name
                    break

    # Also try "Name" field which sometimes contains model names (ai-video-engine)
    if not metadata["model"]:
        name_val = prompt.get("Name", "")
        if isinstance(name_val, str):
            name_lower = name_val.lower()
            for key, name in KNOWN_MODELS.items():
                if key in name_lower:
                    metadata["model"] = name
                    break

    # Infer model from prompt syntax (Midjourney flags in text)
    if not metadata["model"]:
        raw_text = get_best_text(prompt)
        if raw_text:
            mj_flags = re.search(r'--(?:ar|v|style|chaos|no|s|q|iw)\s', raw_text)
            if mj_flags:
                metadata["model"] = "Midjourney"
            else:
                # Check for model name mentions in prompt text
                text_lower = raw_text.lower()
                for key, name in KNOWN_MODELS.items():
                    if key in ("any platform",):
                        continue
                    if key in text_lower:
                        metadata["model"] = name
                        break

    # Get prompt text for content-based categorization
    text = get_best_text(prompt).lower()

    if not text:
        return "general", metadata

    # Determine output type
    video_signals = ["video", "animation", "motion", "footage", "camera", "pan",
                     "zoom", "tracking shot", "drone", "fpv", "montage", "scene"]
    text_signals = ["write", "article", "blog", "copy", "content", "essay",
                    "paraphrase", "storyteller", "ebook"]
    generator_signals = ["prompt generator", "generate prompts", "create prompts",
                         "prompt perfecter"]

    if any(kw in text for kw in generator_signals) or "prompt generator" in type_val.lower():
        metadata["output_type"] = "generator"
        return "generators", metadata
    if any(kw in text for kw in text_signals) or "storyteller" in type_val.lower():
        metadata["output_type"] = "text"
        return "text", metadata

    # Check type_val for video indicators
    video_type_signals = ["video", "sora", "mystic", "cinematic", "music video",
                          "pov", "fpv", "drone", "tracking", "movie", "film",
                          "live-action", "talk show", "podcast", "sitcom",
                          "interview", "reporter"]
    if any(kw in type_val.lower() for kw in video_type_signals):
        metadata["output_type"] = "video"
    elif any(kw in text for kw in video_signals):
        metadata["output_type"] = "video"

    # Word-boundary match helper to avoid substring false positives
    # (e.g., "elf" in "selfie", "cat" in "catch", "car" in "scar")
    def _wb(keyword, txt):
        """Check if keyword exists as a whole word (word-boundary match)."""
        return bool(re.search(r'\b' + re.escape(keyword) + r'\b', txt))

    def _any_wb(keywords, txt):
        """Check if any keyword exists as a whole word."""
        return any(_wb(kw, txt) for kw in keywords)

    # Content category detection (order matters -- more specific first)
    if _any_wb(["logo", "icon", "badge", "emblem", "monogram"], text):
        return "logos-icons", metadata
    if "logo" in type_val.lower():
        return "logos-icons", metadata

    if _any_wb(["superhero", "marvel", "dc comics", "avenger"], text):
        return "superheroes", metadata

    if _any_wb(["anime", "manga", "pixar", "dreamworks", "fortnite",
                "cartoon", "3d render"], text):
        return "animated-3d", metadata

    if _any_wb(["product shot", "packshot", "commercial product",
                "perfume", "sneaker", "shoe", "watch", "bottle"], text):
        return "products", metadata
    if "product" in type_val.lower():
        return "products", metadata

    if _any_wb(["architecture", "building", "interior design",
                "skyscraper", "house", "room"], text):
        return "architecture", metadata

    # Fashion before food-drink to prevent fashion-with-restaurant misclassification
    if _any_wb(["fashion", "outfit", "clothing",
                "runway", "editorial", "vogue", "magazine"], text):
        return "fashion-editorial", metadata
    if "fashion" in type_val.lower() or "editorial" in type_val.lower():
        return "fashion-editorial", metadata

    if (_any_wb(["food", "recipe", "cooking", "cuisine", "chef",
                 "meal", "bakery", "burger", "sushi", "pizza"], text)
            or (_any_wb(["dish", "dessert"], text)
                and "beauty dish" not in text
                and "desolate" not in text)):
        return "food-drink", metadata

    if _any_wb(["car", "vehicle", "automobile", "racing", "motorcycle"], text):
        return "vehicles", metadata
    if "car" in type_val.lower():
        return "vehicles", metadata

    if _any_wb(["dragon", "magic", "medieval", "elf", "wizard",
                "enchanted", "mythical", "fairy"], text):
        return "fantasy", metadata

    if _any_wb(["sci-fi", "futuristic", "cyberpunk", "neon city",
                "robot", "mech", "space station", "dystopian"], text):
        return "sci-fi-futuristic", metadata

    if _any_wb(["landscape", "nature", "scenic", "mountain", "ocean",
                "sunset", "forest", "beach", "waterfall"], text):
        return "landscapes-nature", metadata

    if _any_wb(["portrait", "headshot", "closeup",
                "person"], text):
        return "portraits-people", metadata
    if "person" in type_val.lower():
        return "portraits-people", metadata

    if _any_wb(["abstract", "gradient", "pattern", "texture",
                "wallpaper", "background"], text):
        return "abstract-backgrounds", metadata

    if _any_wb(["t-shirt", "sticker", "coloring book",
                "tattoo", "merch"], text):
        return "print-merchandise", metadata

    # Animals -- specific species names to avoid false positives from
    # "bird's eye view", "creature" (sci-fi), etc.
    if (_any_wb(["animal", "dog", "puppy", "kitten", "horse", "lion",
                 "tiger", "elephant", "whale", "dolphin", "deer", "wolf",
                 "bear", "eagle", "owl", "rabbit", "fox", "wildlife"], text)
            or (_any_wb(["cat", "bird", "fish"], text)
                and "bird's eye" not in text
                and "catsuit" not in text
                and "catapult" not in text)):
        return "animals", metadata

    if metadata["output_type"] == "video":
        return "video-general", metadata

    return "general", metadata


def process_all_tables(input_dir: Path, output_dir: Path) -> dict:
    """Process all scraped tables and extract structured prompts."""
    output_dir.mkdir(parents=True, exist_ok=True)

    all_prompts = []
    table_stats = {}

    # Find all raw JSON files
    raw_files = sorted(input_dir.glob("*.json"))
    raw_files = [f for f in raw_files if f.name != "manifest.json"]

    print(f"Processing {len(raw_files)} raw files...")

    for raw_file in raw_files:
        table_key = raw_file.stem
        print(f"\n--- {table_key} ---")

        with open(raw_file) as f:
            raw_data = json.load(f)

        table_name = raw_data.get("name", table_key)

        # Try API extraction first (structured), fall back to scroll text
        prompts = extract_from_api(raw_data)
        source = "api"

        if not prompts:
            prompts = extract_from_scroll(raw_data)
            source = "scroll"

        # Tag each prompt with source table
        for p in prompts:
            p["_source_table"] = table_key
            p["_source_name"] = table_name

        print(f"  Extracted {len(prompts)} prompts via {source}")
        table_stats[table_key] = {
            "name": table_name,
            "source": source,
            "raw_prompts": len(prompts),
        }

        all_prompts.extend(prompts)

    # Deduplicate
    print(f"\n--- Deduplication ---")
    print(f"Total raw prompts: {len(all_prompts)}")
    unique_prompts, dupes = deduplicate_prompts(all_prompts)
    print(f"Unique prompts: {len(unique_prompts)}")
    print(f"Duplicates removed: {dupes}")

    # Quality filter
    print(f"\n--- Quality Filter ---")
    unique_prompts, noise_removed = filter_noise(unique_prompts)
    print(f"Noise removed: {noise_removed}")
    print(f"Clean prompts: {len(unique_prompts)}")

    # Categorize and enrich with metadata
    print(f"\n--- Categorization ---")
    categories = defaultdict(list)
    models = defaultdict(int)
    output_types = defaultdict(int)

    for prompt in unique_prompts:
        cat, metadata = categorize_prompt(prompt)
        prompt["_category"] = cat
        prompt["_model"] = metadata.get("model")
        prompt["_output_type"] = metadata.get("output_type", "image")
        if metadata.get("styles"):
            prompt["_styles"] = metadata["styles"]
        categories[cat].append(prompt)
        if metadata.get("model"):
            models[metadata["model"]] += 1
        output_types[metadata["output_type"]] += 1

    for cat, cat_prompts in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"  {cat}: {len(cat_prompts)} prompts")

    print(f"\n--- Models ---")
    for model, count in sorted(models.items(), key=lambda x: -x[1]):
        print(f"  {model}: {count}")

    print(f"\n--- Output Types ---")
    for otype, count in sorted(output_types.items(), key=lambda x: -x[1]):
        print(f"  {otype}: {count}")

    # Save by category
    for cat, cat_prompts in categories.items():
        cat_dir = output_dir / cat
        cat_dir.mkdir(parents=True, exist_ok=True)

        cat_file = cat_dir / "prompts.json"
        with open(cat_file, "w") as f:
            json.dump(cat_prompts, f, indent=2, ensure_ascii=False)

    # Save master file
    master_file = output_dir / "all_prompts.json"
    with open(master_file, "w") as f:
        json.dump(unique_prompts, f, indent=2, ensure_ascii=False)

    # Save stats
    stats = {
        "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_raw": len(all_prompts),
        "total_unique": len(unique_prompts),
        "duplicates_removed": dupes,
        "categories": {cat: len(prompts) for cat, prompts in sorted(categories.items(), key=lambda x: -len(x[1]))},
        "models": dict(sorted(models.items(), key=lambda x: -x[1])),
        "output_types": dict(sorted(output_types.items(), key=lambda x: -x[1])),
        "tables": table_stats,
    }
    stats_file = output_dir / "stats.json"
    with open(stats_file, "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\n--- Output ---")
    print(f"Master file: {master_file}")
    print(f"Categories: {len(categories)}")
    print(f"Stats: {stats_file}")

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract structured prompts from Airtable data")
    parser.add_argument("--input", "-i", default="raw", help="Input directory with raw JSON files")
    parser.add_argument("--output", "-o", default="prompts", help="Output directory for processed prompts")
    args = parser.parse_args()

    stats = process_all_tables(Path(args.input), Path(args.output))
    print(json.dumps(stats, indent=2))
