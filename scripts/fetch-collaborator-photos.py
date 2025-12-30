#!/usr/bin/env python3
"""
Fetch Collaborator Photos
=========================

Downloads avatar images from GitHub and Bluesky for collaborators
and saves them locally for faster loading and reliability.

Usage:
    python scripts/fetch-collaborator-photos.py [--dry-run] [--force]

Options:
    --dry-run   Show what would be downloaded without actually downloading
    --force     Re-download even if local file exists
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml


# Configuration
YAML_PATH = "content/collaborators.yml"
OUTPUT_DIR = "content/images/collaborators"
IMAGE_SIZE = 200  # Size for GitHub avatars


def slugify(name: str) -> str:
    """Convert a name to a filename-safe slug."""
    # Lowercase and replace spaces/special chars with hyphens
    slug = name.lower()
    for char in [" ", ".", ",", "'", '"', "(", ")"]:
        slug = slug.replace(char, "-")
    # Remove consecutive hyphens and strip
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def get_github_avatar_url(username: str) -> str:
    """Generate GitHub avatar URL."""
    return f"https://github.com/{username}.png?size={IMAGE_SIZE}"


def get_bluesky_avatar_url(handle: str) -> str | None:
    """Fetch avatar URL from Bluesky public API."""
    try:
        url = f"https://public.api.bsky.app/xrpc/app.bsky.actor.getProfile?actor={handle}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("avatar")
        else:
            print(f"  Warning: Bluesky API returned {response.status_code} for {handle}")
            return None
    except Exception as e:
        print(f"  Warning: Failed to fetch Bluesky profile for {handle}: {e}")
        return None


def download_image(url: str, output_path: Path, dry_run: bool = False) -> bool:
    """Download an image from URL to local path."""
    if dry_run:
        print(f"  Would download: {url}")
        print(f"    -> {output_path}")
        return True

    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()

        # Determine file extension from content-type or URL
        content_type = response.headers.get("content-type", "")
        if "jpeg" in content_type or "jpg" in content_type:
            ext = ".jpg"
        elif "png" in content_type:
            ext = ".png"
        elif "gif" in content_type:
            ext = ".gif"
        elif "webp" in content_type:
            ext = ".webp"
        else:
            # Try to get from URL
            parsed = urlparse(url)
            path_ext = os.path.splitext(parsed.path)[1]
            ext = path_ext if path_ext else ".jpg"

        # Update output path with correct extension
        output_path = output_path.with_suffix(ext)

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"  Downloaded: {output_path}")
        return True

    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False


def get_existing_photo(output_dir: Path, slug: str) -> Path | None:
    """Check if a photo already exists for this person (any extension)."""
    for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        path = output_dir / f"{slug}{ext}"
        if path.exists():
            return path
    return None


def main():
    parser = argparse.ArgumentParser(description="Fetch collaborator photos")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--force", action="store_true", help="Re-download existing files")
    args = parser.parse_args()

    # Find project root (where this script is in scripts/)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    yaml_path = project_root / YAML_PATH
    output_dir = project_root / OUTPUT_DIR

    if not yaml_path.exists():
        print(f"Error: YAML file not found: {yaml_path}")
        sys.exit(1)

    # Load YAML
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    people = data.get("people", [])
    print(f"Found {len(people)} collaborators in {yaml_path.name}")
    print(f"Output directory: {output_dir}")
    print()

    stats = {"downloaded": 0, "skipped": 0, "failed": 0, "no_source": 0}

    for person in people:
        name = person.get("name", "Unknown")
        slug = slugify(name)
        links = person.get("links", {})

        print(f"Processing: {name}")

        # Check if already has explicit local photo
        existing_photo = person.get("photo")
        if existing_photo and existing_photo.startswith("/images/"):
            print(f"  Already has local photo: {existing_photo}")
            stats["skipped"] += 1
            continue

        # Check if local file already exists
        existing_file = get_existing_photo(output_dir, slug)
        if existing_file and not args.force:
            print(f"  Already exists: {existing_file.name}")
            stats["skipped"] += 1
            continue

        # Determine source URL (priority: GitHub > Bluesky)
        source_url = None
        source_type = None

        if links.get("github"):
            source_url = get_github_avatar_url(links["github"])
            source_type = "GitHub"
        elif links.get("bluesky"):
            source_url = get_bluesky_avatar_url(links["bluesky"])
            source_type = "Bluesky"

        if not source_url:
            print("  No GitHub or Bluesky profile found")
            stats["no_source"] += 1
            continue

        print(f"  Source: {source_type} ({links.get('github') or links.get('bluesky')})")

        # Download
        output_path = output_dir / f"{slug}.jpg"  # Extension will be corrected
        if download_image(source_url, output_path, dry_run=args.dry_run):
            stats["downloaded"] += 1
        else:
            stats["failed"] += 1

    # Summary
    print()
    print("=" * 50)
    print("Summary:")
    print(f"  Downloaded: {stats['downloaded']}")
    print(f"  Skipped (existing): {stats['skipped']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  No source available: {stats['no_source']}")

    if not args.dry_run and stats["downloaded"] > 0:
        print()
        print("Next steps:")
        print("1. Review downloaded images in content/images/collaborators/")
        print("2. Update collaborators.yml to use local paths:")
        print('   photo: "/images/collaborators/person-name.jpg"')
        print("3. Or run with --update-yaml to auto-update (coming soon)")


if __name__ == "__main__":
    main()
