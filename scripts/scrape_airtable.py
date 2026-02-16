#!/usr/bin/env python3
"""
Airtable Shared View Scraper v2
Extracts all rows from Airtable shared views using Playwright.
Uses route-based interception + aggressive scrolling + raw text parsing.

Usage: python scrape_airtable.py [--single KEY] [--output DIR]
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


TABLES = {
    # Add your Airtable shared view URLs here.
    # Format: "key": {"url": "https://airtable.com/app.../shr.../tbl.../viw...", "name": "Display Name"}
    #
    # Example:
    # "my-prompts": {
    #     "url": "https://airtable.com/appXXX/shrXXX/tblXXX/viwXXX",
    #     "name": "My Prompt Collection",
    # },
}


def extract_ids_from_url(url: str) -> dict:
    """Extract app, share, table, and view IDs from Airtable URL."""
    parts = urlparse(url).path.strip("/").split("/")
    ids = {}
    for part in parts:
        if part.startswith("app"):
            ids["app_id"] = part
        elif part.startswith("shr"):
            ids["share_id"] = part
        elif part.startswith("tbl"):
            ids["table_id"] = part
        elif part.startswith("viw"):
            ids["view_id"] = part
    return ids


def collect_all_text_and_images(page) -> dict:
    """Extract all visible text and image URLs from the current page state."""
    return page.evaluate(r"""() => {
        const texts = new Set();
        const images = new Set();

        // Collect all text nodes
        const walker = document.createTreeWalker(
            document.body,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        while (walker.nextNode()) {
            const text = walker.currentNode.textContent.trim();
            if (text && text.length > 1) texts.add(text);
        }

        // Collect all images (excluding icons/avatars)
        document.querySelectorAll('img').forEach(img => {
            const src = img.src || img.dataset?.src || '';
            if (src && !src.includes('avatar') && !src.includes('icon') &&
                !src.includes('logo') && src.length > 20) {
                images.add(src);
            }
        });

        // Also check background images
        document.querySelectorAll('[style*="background-image"]').forEach(el => {
            const match = el.style.backgroundImage.match(/url\(["']?(.+?)["']?\)/);
            if (match) images.add(match[1]);
        });

        return {
            texts: Array.from(texts),
            images: Array.from(images),
        };
    }""")


def aggressive_scroll_and_collect(page, table_key: str) -> dict:
    """Scroll through the entire page collecting all text and images."""
    all_texts = set()
    all_images = set()
    stale_rounds = 0
    max_stale = 5
    scroll_count = 0
    max_scrolls = 300

    print(f"  Scrolling to load all content...")

    # First, find the best scroll container
    scroll_selector = page.evaluate(r"""() => {
        // Airtable uses various scrollable containers
        const candidates = [
            '.antiscroll-inner',
            '[class*="scrollable"]',
            '[class*="Scrollable"]',
            '[data-testid="view-container"]',
            'main',
            '.sharedViewBody',
            '[class*="SharedView"]',
            '[class*="sharedView"]',
        ];
        for (const sel of candidates) {
            const el = document.querySelector(sel);
            if (el && el.scrollHeight > el.clientHeight + 100) {
                return sel;
            }
        }
        // Fallback: find the tallest scrollable element
        let best = null;
        let bestHeight = 0;
        document.querySelectorAll('div').forEach(el => {
            if (el.scrollHeight > el.clientHeight + 200 && el.scrollHeight > bestHeight) {
                bestHeight = el.scrollHeight;
                // Generate a unique selector
                if (el.id) best = '#' + el.id;
                else if (el.className) {
                    const cls = el.className.split(' ')[0];
                    if (cls) best = '.' + cls;
                }
            }
        });
        return best;
    }""")

    print(f"  Scroll container: {scroll_selector or 'window'}")

    while scroll_count < max_scrolls:
        # Collect current state
        data = collect_all_text_and_images(page)
        new_texts = set(data["texts"]) - all_texts
        new_images = set(data["images"]) - all_images

        all_texts.update(new_texts)
        all_images.update(new_images)

        if not new_texts and not new_images:
            stale_rounds += 1
            if stale_rounds >= max_stale:
                print(f"  No new content after {max_stale} scrolls. Done.")
                break
        else:
            stale_rounds = 0

        # Scroll down
        if scroll_selector:
            page.evaluate("""(sel) => {
                const el = document.querySelector(sel);
                if (el) el.scrollTop += 800;
            }""", scroll_selector)
        else:
            page.evaluate("window.scrollBy(0, 800)")

        page.wait_for_timeout(300)
        scroll_count += 1

        if scroll_count % 20 == 0:
            print(f"  ... scrolled {scroll_count}x, {len(all_texts)} texts, {len(all_images)} images")

    print(f"  Final: {len(all_texts)} text items, {len(all_images)} images after {scroll_count} scrolls")

    return {
        "texts": sorted(all_texts),
        "images": sorted(all_images),
    }


def scrape_single_table(browser, table_key: str, table_info: dict, output_dir: Path) -> dict:
    """Scrape a single Airtable shared view."""
    url = table_info["url"]
    name = table_info["name"]
    print(f"\n{'='*60}")
    print(f"[{table_key}] {name}")
    print(f"{'='*60}")

    ids = extract_ids_from_url(url)
    captured_api = []

    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    )
    page = context.new_page()

    # Set up route-based interception BEFORE navigation
    def capture_response(route):
        """Intercept and capture API responses while letting them through."""
        response = route.fetch()
        resp_url = route.request.url
        try:
            body = response.json()
            captured_api.append({
                "url": resp_url,
                "status": response.status,
                "data": body,
            })
            print(f"  [API] Captured: {resp_url[:80]}...")
        except Exception:
            pass
        route.fulfill(response=response)

    # Intercept Airtable API calls
    page.route("**/v0.3/**", capture_response)
    page.route("**/api/**", capture_response)
    page.route("**readSharedViewData**", capture_response)
    page.route("**readData**", capture_response)

    result = {
        "key": table_key,
        "name": name,
        "url": url,
        "ids": ids,
        "api_data": None,
        "scroll_data": None,
        "status": "pending",
    }

    try:
        # Navigate
        print(f"  Loading page...")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Wait for content to render
        page.wait_for_timeout(8000)

        # Check for any cookie/consent dialogs and dismiss
        try:
            page.evaluate(r"""() => {
                // Click away any overlays
                document.querySelectorAll('[class*="cookie"], [class*="consent"], [class*="banner"]').forEach(el => {
                    const btn = el.querySelector('button');
                    if (btn) btn.click();
                });
            }""")
        except Exception:
            pass

        # Save API data if captured
        if captured_api:
            result["api_data"] = captured_api
            print(f"  Captured {len(captured_api)} API responses")

        # Scroll and collect everything
        scroll_data = aggressive_scroll_and_collect(page, table_key)
        result["scroll_data"] = scroll_data

        # Take screenshot
        screenshot_path = output_dir / f"{table_key}.png"
        page.screenshot(path=str(screenshot_path), full_page=False)

        has_content = (
            len(scroll_data.get("texts", [])) > 10
            or len(scroll_data.get("images", [])) > 0
            or len(captured_api) > 0
        )
        result["status"] = "success" if has_content else "minimal_data"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"  [ERROR] {e}", file=sys.stderr)
    finally:
        context.close()

    # Save raw result
    output_file = output_dir / f"{table_key}.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"  Saved: {output_file.name} ({result['status']})")

    return result


def main(args):
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.single:
        tables_to_scrape = {args.single: TABLES[args.single]}
    else:
        tables_to_scrape = TABLES

    manifest = {
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tables": len(tables_to_scrape),
        "results": {},
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for table_key, table_info in tables_to_scrape.items():
            result = scrape_single_table(browser, table_key, table_info, output_dir)
            manifest["results"][table_key] = {
                "name": table_info["name"],
                "status": result["status"],
                "text_count": len(result.get("scroll_data", {}).get("texts", [])),
                "image_count": len(result.get("scroll_data", {}).get("images", [])),
                "api_responses": len(result.get("api_data") or []),
            }

        browser.close()

    # Save manifest
    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print("SCRAPING SUMMARY")
    print(f"{'='*60}")
    total_texts = 0
    total_images = 0
    for key, info in manifest["results"].items():
        icon = "OK" if info["status"] == "success" else "!!"
        print(f"  [{icon}] {info['name']}: {info['text_count']} texts, {info['image_count']} images, {info['api_responses']} API")
        total_texts += info["text_count"]
        total_images += info["image_count"]

    print(f"\n  TOTAL: {total_texts} text items, {total_images} images")
    print(f"  Output: {output_dir.resolve()}")

    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Airtable shared views")
    parser.add_argument("--single", help="Scrape only this table key (e.g. mega-prompts-1)")
    parser.add_argument("--output", "-o", default="raw", help="Output directory")
    args = parser.parse_args()
    main(args)
