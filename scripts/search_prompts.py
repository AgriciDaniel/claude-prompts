#!/usr/bin/env python3
"""
Prompt Database Search
Fast search through the curated prompt database.

Usage:
  python search_prompts.py "query"                    # Full-text search
  python search_prompts.py --category fantasy          # Browse category
  python search_prompts.py --model Midjourney           # Filter by model
  python search_prompts.py --type video                 # Filter by output type
  python search_prompts.py --stats                      # Show database stats
  python search_prompts.py --categories                 # List all categories
  python search_prompts.py --random                     # Random prompt
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "prompts"
MASTER_FILE = DB_PATH / "all_prompts.json"
STATS_FILE = DB_PATH / "stats.json"


def load_prompts() -> list[dict]:
    """Load the master prompt database."""
    if not MASTER_FILE.exists():
        print(json.dumps({"error": f"Database not found: {MASTER_FILE}"}))
        sys.exit(1)
    with open(MASTER_FILE) as f:
        return json.load(f)


def load_stats() -> dict:
    """Load database statistics."""
    if not STATS_FILE.exists():
        return {}
    with open(STATS_FILE) as f:
        return json.load(f)


def get_prompt_text(prompt: dict) -> str:
    """Extract the main text content from a prompt record."""
    for key in ("Prompt", "prompt", "Full Prompt", "\U0001f916Full Prompt",
                "Extract Prompt", "Description", "description",
                "Prompt Example", "\U0001f4ddQuick Description", "Text", "text"):
        if key in prompt and isinstance(prompt[key], str) and len(prompt[key]) > 10:
            return prompt[key]
    # Fallback: find longest string value
    longest = ""
    for k, v in prompt.items():
        if isinstance(v, str) and len(v) > len(longest) and not k.startswith("_"):
            longest = v
    return longest


def search_prompts(query: str, prompts: list[dict], category: str = None,
                   model: str = None, output_type: str = None,
                   limit: int = 10) -> list[dict]:
    """Search prompts with optional filters."""
    results = []
    query_lower = query.lower() if query else ""
    query_words = query_lower.split() if query_lower else []

    for prompt in prompts:
        # Apply filters
        if category and prompt.get("_category", "").lower() != category.lower():
            continue
        if model and (prompt.get("_model") or "").lower() != model.lower():
            continue
        if output_type and prompt.get("_output_type", "").lower() != output_type.lower():
            continue

        # Text search
        if query_words:
            text = get_prompt_text(prompt).lower()
            # Also search in tags, styles, name
            tags = " ".join(prompt.get("Tags/Styles", []) if isinstance(prompt.get("Tags/Styles"), list) else [])
            tags += " " + " ".join(prompt.get("_styles", []) if isinstance(prompt.get("_styles"), list) else [])
            name = str(prompt.get("Name", "")).lower()
            searchable = f"{text} {tags.lower()} {name}"

            score = 0
            for word in query_words:
                if word in searchable:
                    score += 1
                    # Bonus for exact phrase match
                    if query_lower in searchable:
                        score += 2

            if score == 0:
                continue

            results.append((score, prompt))
        else:
            # No query, just filters
            results.append((0, prompt))

    # Sort by relevance if searching
    if query_words:
        results.sort(key=lambda x: x[0], reverse=True)

    return [prompt for _, prompt in results[:limit]]


def format_prompt(prompt: dict, index: int = None, full: bool = False) -> dict:
    """Format a prompt for output."""
    text = get_prompt_text(prompt)
    result = {
        "prompt": text if full else (text[:200] + "..." if len(text) > 200 else text),
        "category": prompt.get("_category", "unknown"),
        "model": prompt.get("_model"),
        "output_type": prompt.get("_output_type", "image"),
        "source": prompt.get("_source_name"),
    }
    if index is not None:
        result["index"] = index + 1

    # Add optional fields
    tags = prompt.get("Tags/Styles") or prompt.get("_styles")
    if tags:
        result["tags"] = tags if isinstance(tags, list) else [tags]

    name = prompt.get("Name")
    if name and isinstance(name, str):
        result["name"] = name

    # Add image info
    image = prompt.get("Image") or prompt.get("Still Shot/Video")
    if isinstance(image, list) and image:
        result["has_image"] = True
        result["image_url"] = image[0].get("url", "") if isinstance(image[0], dict) else ""

    return result


def show_stats():
    """Display database statistics."""
    stats = load_stats()
    output = {
        "total_prompts": stats.get("total_unique", 0),
        "categories": stats.get("categories", {}),
        "models": stats.get("models", {}),
        "output_types": stats.get("output_types", {}),
        "sources": {k: v["raw_prompts"] for k, v in stats.get("tables", {}).items()},
    }
    return output


def show_categories():
    """List all available categories."""
    stats = load_stats()
    return {"categories": stats.get("categories", {})}


def random_prompt(prompts: list[dict], category: str = None, model: str = None) -> dict:
    """Get a random prompt."""
    filtered = prompts
    if category:
        filtered = [p for p in filtered if p.get("_category", "").lower() == category.lower()]
    if model:
        filtered = [p for p in filtered if (p.get("_model") or "").lower() == model.lower()]
    if not filtered:
        return {"error": "No prompts match the filters"}
    choice = random.choice(filtered)
    return format_prompt(choice, full=True)


def main():
    parser = argparse.ArgumentParser(description="Search the prompt database")
    parser.add_argument("query", nargs="?", default="", help="Search query")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--model", "-m", help="Filter by AI model")
    parser.add_argument("--type", "-t", help="Filter by output type (image/video/text/generator)")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    parser.add_argument("--stats", action="store_true", help="Show database stats")
    parser.add_argument("--categories", action="store_true", help="List categories")
    parser.add_argument("--random", action="store_true", help="Get random prompt")
    parser.add_argument("--full", action="store_true", help="Show full prompt text")
    args = parser.parse_args()

    if args.stats:
        print(json.dumps(show_stats(), indent=2))
        return

    if args.categories:
        print(json.dumps(show_categories(), indent=2))
        return

    prompts = load_prompts()

    if args.random:
        result = random_prompt(prompts, args.category, args.model)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # Search
    results = search_prompts(
        args.query, prompts,
        category=args.category,
        model=args.model,
        output_type=args.type,
        limit=args.limit,
    )

    output = {
        "query": args.query or None,
        "filters": {
            "category": args.category,
            "model": args.model,
            "type": args.type,
        },
        "count": len(results),
        "results": [format_prompt(p, i, full=args.full) for i, p in enumerate(results)],
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
