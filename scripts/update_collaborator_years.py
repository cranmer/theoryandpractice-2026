#!/usr/bin/env python
"""
Update collaborator start_year and end_year based on co-authored publications.

Usage:
    python scripts/update_collaborator_years.py [--dry-run]

Searches OpenAlex API to find papers co-authored with Kyle Cranmer for each
collaborator and updates start_year/end_year based on first/last publication.

Only updates fields that are not already set.
"""

import argparse
import json
import os
import re
import time
import urllib.request
import urllib.parse
from pathlib import Path

import yaml

# Kyle Cranmer's OpenAlex author ID
KYLE_CRANMER_OPENALEX_ID = "A5108167175"

# OpenAlex API endpoint
OPENALEX_API = "https://api.openalex.org"

# Be polite - identify ourselves
USER_AGENT = "TheoryAndPractice/1.0 (https://theoryandpractice.org; mailto:kyle.cranmer@wisc.edu)"


def normalize_name(name):
    """Normalize a name for matching."""
    # Remove accents and special characters for matching
    name = name.lower().strip()
    # Handle common accent variations
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a', 'ã': 'a',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o', 'õ': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ñ': 'n', 'ç': 'c', 'ø': 'o', 'å': 'a', 'æ': 'ae',
        'ß': 'ss', 'š': 's', 'ž': 'z', 'ý': 'y', 'ÿ': 'y',
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    return name


def search_openalex_author(name):
    """Search for an author in OpenAlex by name."""
    query = urllib.parse.quote(name)
    url = f"{OPENALEX_API}/authors?search={query}&per_page=5"

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', USER_AGENT)

        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            results = data.get('results', [])
            if results:
                # Return first match - could be improved with better matching
                return results[0]
    except Exception as e:
        pass

    return None


def get_coauthored_works(author_id, kyle_id=KYLE_CRANMER_OPENALEX_ID):
    """Get works co-authored by the given author and Kyle Cranmer."""
    # Search for works where both authors are listed
    # OpenAlex filter: authorships.author.id
    filter_str = f"authorships.author.id:{author_id},authorships.author.id:{kyle_id}"
    url = f"{OPENALEX_API}/works?filter={filter_str}&per_page=200&sort=publication_year:asc"

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', USER_AGENT)

        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('results', [])
    except Exception as e:
        return []


def get_collaboration_years(collaborator_name):
    """
    Find the first and last year of co-authored papers with Kyle Cranmer.

    Returns (start_year, end_year, num_papers) or (None, None, 0) if not found.
    """
    # Search for the author
    author = search_openalex_author(collaborator_name)
    if not author:
        return None, None, 0

    author_id = author.get('id', '').replace('https://openalex.org/', '')
    if not author_id:
        return None, None, 0

    # Get co-authored works
    works = get_coauthored_works(author_id)
    if not works:
        return None, None, 0

    # Extract years
    years = []
    for work in works:
        year = work.get('publication_year')
        if year:
            years.append(year)

    if not years:
        return None, None, 0

    return min(years), max(years), len(years)


def load_yaml_preserve_style(yaml_path):
    """Load YAML file content as text for manual editing."""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return f.read()


def update_yaml_entry(content, name, start_year=None, end_year=None):
    """
    Update a collaborator entry in the YAML content.
    Only adds fields if they don't already exist.
    """
    # Find the entry for this person
    # Pattern to match the person's entry block
    # We look for "- name: "Name"" and then the subsequent fields

    # Escape special regex characters in name
    escaped_name = re.escape(name)

    # Pattern to find the entry
    pattern = rf'(- name: ["\']?{escaped_name}["\']?\n)'
    match = re.search(pattern, content)

    if not match:
        return content, False

    # Find where this entry ends (next entry starting with "  - name:" or end of people section)
    entry_start = match.start()

    # Find the next entry or end
    next_entry = re.search(r'\n  - name:', content[match.end():])
    if next_entry:
        entry_end = match.end() + next_entry.start()
    else:
        entry_end = len(content)

    entry_text = content[entry_start:entry_end]
    original_entry = entry_text

    modified = False

    # Check and add start_year if not present
    if start_year and 'start_year:' not in entry_text:
        # Find a good place to insert (after affiliation or role)
        insert_patterns = [
            (r'(    current_position: [^\n]+\n)', r'\1    start_year: ' + str(start_year) + '\n'),
            (r'(    affiliation: [^\n]+\n)', r'\1    start_year: ' + str(start_year) + '\n'),
            (r'(    role: [^\n]+\n)', r'\1    start_year: ' + str(start_year) + '\n'),
            (r'(    current: [^\n]+\n)', r'\1    start_year: ' + str(start_year) + '\n'),
        ]
        for pattern, replacement in insert_patterns:
            if re.search(pattern, entry_text):
                entry_text = re.sub(pattern, replacement, entry_text, count=1)
                modified = True
                break

    # Check and add end_year if not present and collaboration has ended
    # We consider it ended if the last paper was more than 2 years ago
    import datetime
    current_year = datetime.datetime.now().year

    if end_year and 'end_year:' not in entry_text:
        # Only add end_year if last collaboration was > 2 years ago
        if end_year < current_year - 1:
            # Find start_year line and add end_year after it
            if 'start_year:' in entry_text:
                entry_text = re.sub(
                    r'(    start_year: \d+\n)',
                    r'\1    end_year: ' + str(end_year) + '\n',
                    entry_text,
                    count=1
                )
                modified = True
            else:
                # Add after current_position or affiliation
                insert_patterns = [
                    (r'(    current_position: [^\n]+\n)', r'\1    end_year: ' + str(end_year) + '\n'),
                    (r'(    affiliation: [^\n]+\n)', r'\1    end_year: ' + str(end_year) + '\n'),
                ]
                for pattern, replacement in insert_patterns:
                    if re.search(pattern, entry_text):
                        entry_text = re.sub(pattern, replacement, entry_text, count=1)
                        modified = True
                        break

    # Also update current: false if end_year was added
    if modified and end_year and end_year < current_year - 1:
        if 'current: true' in entry_text:
            entry_text = entry_text.replace('current: true', 'current: false')

    if modified:
        content = content[:entry_start] + entry_text + content[entry_end:]

    return content, modified


def main():
    parser = argparse.ArgumentParser(description='Update collaborator years from OpenAlex')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    args = parser.parse_args()

    # Find the project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    yaml_path = project_root / 'content' / 'collaborators.yml'
    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found")
        return

    # Load YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # Load raw content for editing
    content = load_yaml_preserve_style(yaml_path)

    people = data.get('people', [])
    print(f"Found {len(people)} collaborators to process...")

    updated_count = 0
    skipped_count = 0
    not_found_count = 0

    for i, person in enumerate(people):
        name = person.get('name', '')
        category = person.get('category', '')

        # Skip if already has both years
        has_start = person.get('start_year') is not None
        has_end = person.get('end_year') is not None

        if has_start and has_end:
            skipped_count += 1
            continue

        print(f"  [{i+1}/{len(people)}] {name}...", end=" ", flush=True)

        # Search OpenAlex
        start_year, end_year, num_papers = get_collaboration_years(name)

        if num_papers == 0:
            print("no co-authored papers found")
            not_found_count += 1
            time.sleep(0.2)
            continue

        # Update content
        content, modified = update_yaml_entry(
            content,
            name,
            start_year=start_year if not has_start else None,
            end_year=end_year if not has_end else None
        )

        if modified:
            print(f"{num_papers} papers, {start_year}-{end_year}")
            updated_count += 1
        else:
            print(f"{num_papers} papers (already set)")
            skipped_count += 1

        # Be polite to the API
        time.sleep(0.3)

    print(f"\nSummary:")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped (already set): {skipped_count}")
    print(f"  Not found: {not_found_count}")

    if args.dry_run:
        print("\n[DRY RUN] No changes written to file.")
        if updated_count > 0:
            print("Run without --dry-run to apply changes.")
    else:
        if updated_count > 0:
            with open(yaml_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\nSaved changes to {yaml_path}")
        else:
            print("\nNo changes to save.")


if __name__ == '__main__':
    main()
