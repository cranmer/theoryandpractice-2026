#!/usr/bin/env python3
"""
Search Media Mentions
=====================

Search for new media mentions and articles about Kyle Cranmer
using Google Search API (via SerpAPI) or web scraping.

Usage:
    python scripts/search_media.py [--dry-run] [--days N]

Options:
    --dry-run   Show results without saving
    --days N    Search for articles from the last N days (default: 30)
    --output    Save suggestions to a file

Requirements:
    pip install requests beautifulsoup4 pyyaml

Optional (for better results):
    pip install serpapi  # Requires SERPAPI_KEY environment variable
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import requests
import yaml

# Configuration
YAML_PATH = "content/media.yml"
SEARCH_QUERIES = [
    '"Kyle Cranmer" physics',
    '"Kyle Cranmer" AI',
    '"Kyle Cranmer" machine learning',
    '"Kyle Cranmer" ATLAS',
    '"Kyle Cranmer" LHC',
    '"Kyle Cranmer" Wisconsin',
]

# Known domains to prioritize
PRIORITY_DOMAINS = [
    "nytimes.com",
    "wired.com",
    "vox.com",
    "newyorker.com",
    "theguardian.com",
    "bbc.com",
    "npr.org",
    "scientificamerican.com",
    "quantamagazine.org",
    "nature.com",
    "science.org",
    "phys.org",
    "symmetrymagazine.org",
    "cerncourier.com",
]

# Domains to exclude (often irrelevant)
EXCLUDED_DOMAINS = [
    "linkedin.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",  # We handle YouTube separately via embed
    "github.com",
    "arxiv.org",
    "inspirehep.net",
    "scholar.google.com",
    "researchgate.net",
    "academia.edu",
]


def load_existing_media(yaml_path: Path) -> dict:
    """Load existing media items to avoid duplicates."""
    if not yaml_path.exists():
        return {"items": [], "urls": set()}

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    items = data.get("items", [])
    urls = {item.get("url", "") for item in items if item.get("url")}

    return {"items": items, "urls": urls}


def normalize_url(url: str) -> str:
    """Normalize URL for comparison."""
    # Remove tracking parameters and normalize
    parsed = urlparse(url)
    # Remove common tracking params
    path = parsed.path.rstrip("/")
    return f"{parsed.netloc}{path}".lower()


def is_duplicate(url: str, existing_urls: set) -> bool:
    """Check if URL is already in existing media."""
    normalized = normalize_url(url)
    for existing in existing_urls:
        if normalized in normalize_url(existing) or normalize_url(existing) in normalized:
            return True
    return False


def search_google_news(query: str, days: int = 30) -> list:
    """
    Search Google News for recent articles.
    Uses requests to fetch Google News RSS or search results.
    """
    results = []

    # Try Google News RSS
    try:
        # Google News RSS feed
        encoded_query = quote_plus(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

        response = requests.get(rss_url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })

        if response.status_code == 200:
            # Simple XML parsing for RSS
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            for item in root.findall(".//item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                pubdate_elem = item.find("pubDate")
                source_elem = item.find("source")

                if title_elem is not None and link_elem is not None:
                    title = title_elem.text or ""
                    link = link_elem.text or ""
                    source = source_elem.text if source_elem is not None else ""
                    pubdate = pubdate_elem.text if pubdate_elem is not None else ""

                    # Parse date
                    date = None
                    if pubdate:
                        try:
                            # RFC 822 format
                            date = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
                        except ValueError:
                            try:
                                date = datetime.strptime(pubdate[:25], "%a, %d %b %Y %H:%M:%S")
                            except ValueError:
                                pass

                    # Check if within date range
                    if date:
                        cutoff = datetime.now() - timedelta(days=days)
                        if date < cutoff:
                            continue

                    results.append({
                        "title": title,
                        "url": link,
                        "source": source,
                        "date": date,
                        "query": query,
                    })
    except Exception as e:
        print(f"  Warning: Google News search failed for '{query}': {e}")

    return results


def search_with_serpapi(query: str, days: int = 30) -> list:
    """
    Search using SerpAPI (requires SERPAPI_KEY).
    More reliable but requires API key.
    """
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        return []

    results = []

    try:
        url = "https://serpapi.com/search"
        params = {
            "api_key": api_key,
            "engine": "google",
            "q": query,
            "tbm": "nws",  # News search
            "num": 20,
        }

        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("news_results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "source": item.get("source", ""),
                    "date": None,  # SerpAPI provides relative dates
                    "snippet": item.get("snippet", ""),
                    "query": query,
                })
    except Exception as e:
        print(f"  Warning: SerpAPI search failed: {e}")

    return results


def categorize_result(result: dict) -> str:
    """Guess the category based on source and content."""
    url = result.get("url", "").lower()
    source = result.get("source", "").lower()
    title = result.get("title", "").lower()

    # Video platforms
    if "youtube" in url or "vimeo" in url:
        return "videos"

    # Podcast indicators
    if any(word in title or word in source for word in ["podcast", "episode", "listen"]):
        return "podcasts"

    # Interview indicators
    if any(word in title for word in ["interview", "q&a", "talks to", "speaks with"]):
        return "interviews"

    # Default to articles
    return "articles"


def format_yaml_entry(result: dict) -> dict:
    """Format a search result as a YAML media entry."""
    category = categorize_result(result)

    entry = {
        "title": result.get("title", "").strip(),
        "outlet": result.get("source", "Unknown"),
        "category": category,
        "url": result.get("url", ""),
    }

    if result.get("date"):
        entry["date"] = result["date"].strftime("%Y-%m-%d")

    if result.get("snippet"):
        # Clean up snippet
        snippet = result["snippet"][:200]
        if len(result.get("snippet", "")) > 200:
            snippet += "..."
        entry["description"] = snippet

    return entry


def main():
    parser = argparse.ArgumentParser(description="Search for media mentions")
    parser.add_argument("--dry-run", action="store_true", help="Show results without saving")
    parser.add_argument("--days", type=int, default=30, help="Search last N days (default: 30)")
    parser.add_argument("--output", type=str, help="Output file for suggestions")
    args = parser.parse_args()

    # Find project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    yaml_path = project_root / YAML_PATH

    print(f"Searching for media mentions (last {args.days} days)")
    print("=" * 60)

    # Load existing media
    existing = load_existing_media(yaml_path)
    print(f"Found {len(existing['items'])} existing media items")
    print()

    # Collect all results
    all_results = []

    # Check for SerpAPI
    has_serpapi = bool(os.environ.get("SERPAPI_KEY"))
    if has_serpapi:
        print("Using SerpAPI for search (SERPAPI_KEY found)")
    else:
        print("Using Google News RSS (set SERPAPI_KEY for better results)")
    print()

    # Run searches
    for query in SEARCH_QUERIES:
        print(f"Searching: {query}")

        if has_serpapi:
            results = search_with_serpapi(query, args.days)
        else:
            results = search_google_news(query, args.days)

        print(f"  Found {len(results)} results")
        all_results.extend(results)

    print()
    print(f"Total raw results: {len(all_results)}")

    # Deduplicate and filter
    seen_urls = set()
    filtered_results = []

    for result in all_results:
        url = result.get("url", "")

        # Skip if no URL
        if not url:
            continue

        # Skip excluded domains
        domain = urlparse(url).netloc.lower()
        if any(excluded in domain for excluded in EXCLUDED_DOMAINS):
            continue

        # Skip if already in media.yml
        if is_duplicate(url, existing["urls"]):
            continue

        # Skip if already seen in this search
        normalized = normalize_url(url)
        if normalized in seen_urls:
            continue

        seen_urls.add(normalized)

        # Mark priority sources
        is_priority = any(priority in domain for priority in PRIORITY_DOMAINS)
        result["priority"] = is_priority

        filtered_results.append(result)

    # Sort by priority then date
    filtered_results.sort(key=lambda x: (not x.get("priority", False), x.get("date") or datetime.min), reverse=True)

    print(f"After filtering: {len(filtered_results)} new potential items")
    print()

    if not filtered_results:
        print("No new media mentions found!")
        return

    # Display results
    print("=" * 60)
    print("SUGGESTED ADDITIONS TO media.yml")
    print("=" * 60)
    print()

    suggestions = []
    for i, result in enumerate(filtered_results[:20], 1):  # Top 20
        entry = format_yaml_entry(result)
        suggestions.append(entry)

        priority_marker = " *PRIORITY*" if result.get("priority") else ""
        print(f"{i}. [{entry['category'].upper()}] {entry['title'][:60]}...{priority_marker}")
        print(f"   Source: {entry['outlet']}")
        print(f"   URL: {entry['url'][:80]}...")
        if entry.get("date"):
            print(f"   Date: {entry['date']}")
        print()

    # Output YAML
    if suggestions:
        yaml_output = yaml.dump(suggestions, default_flow_style=False, allow_unicode=True, sort_keys=False)

        print("=" * 60)
        print("YAML FORMAT (copy to media.yml items section):")
        print("=" * 60)
        print()
        print(yaml_output)

        if args.output:
            output_path = Path(args.output)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("# Suggested media items from search\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Search period: last {args.days} days\n\n")
                f.write(yaml_output)
            print(f"Saved suggestions to: {output_path}")

    print()
    print("Review the suggestions above and add relevant items to content/media.yml")


if __name__ == "__main__":
    main()
