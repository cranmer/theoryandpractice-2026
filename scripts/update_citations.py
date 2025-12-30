#!/usr/bin/env python
"""
Fetch citation counts from OpenAlex API for selected publications.

Usage:
    python scripts/update_citations.py

Reads DOIs and arXiv IDs from the BibTeX file referenced in selected-publications.yml
and fetches citation counts from OpenAlex. Results are cached in content/citations.json.
"""

import json
import os
import time
import urllib.request
import urllib.parse
from pathlib import Path

import yaml

# OpenAlex API endpoint
OPENALEX_API = "https://api.openalex.org/works"

# Be polite - identify ourselves
USER_AGENT = "TheoryAndPractice/1.0 (https://theoryandpractice.org; mailto:kyle.cranmer@wisc.edu)"


def fetch_from_openalex(doi=None, arxiv_id=None):
    """Fetch citation count from OpenAlex for a given DOI or arXiv ID."""
    if doi:
        url = f"{OPENALEX_API}/doi:{doi}"
    elif arxiv_id:
        clean_arxiv = arxiv_id.replace('arXiv:', '').strip()
        url = f"{OPENALEX_API}/arxiv:{clean_arxiv}"
    else:
        return None

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', USER_AGENT)

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return {
                'cited_by_count': data.get('cited_by_count', 0),
                'openalex_id': data.get('id', ''),
                'source': 'openalex',
            }
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None


# Semantic Scholar API endpoint
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper"


def fetch_from_semantic_scholar(doi=None, arxiv_id=None):
    """Fetch citation count from Semantic Scholar as fallback."""
    if doi:
        url = f"{SEMANTIC_SCHOLAR_API}/DOI:{doi}?fields=citationCount,externalIds"
    elif arxiv_id:
        clean_arxiv = arxiv_id.replace('arXiv:', '').strip()
        url = f"{SEMANTIC_SCHOLAR_API}/ARXIV:{clean_arxiv}?fields=citationCount,externalIds"
    else:
        return None

    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', USER_AGENT)

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            paper_id = data.get('paperId', '')
            return {
                'cited_by_count': data.get('citationCount', 0),
                'semantic_scholar_id': f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else '',
                'source': 'semantic_scholar',
            }
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None


def fetch_citation_count(doi=None, arxiv_id=None):
    """Fetch citation count, trying OpenAlex first, then Semantic Scholar."""
    # Try OpenAlex first
    result = fetch_from_openalex(doi=doi, arxiv_id=arxiv_id)
    if result:
        return result

    # Fallback to Semantic Scholar
    result = fetch_from_semantic_scholar(doi=doi, arxiv_id=arxiv_id)
    if result:
        return result

    return None


def load_bibtex_entries(bibtex_path):
    """Load BibTeX entries and extract DOI/arXiv IDs."""
    try:
        from pybtex.database.input.bibtex import Parser
        bibdata = Parser().parse_file(bibtex_path)
    except ImportError:
        print("pybtex not installed. Run: pip install pybtex")
        return {}
    except Exception as e:
        print(f"Error parsing BibTeX: {e}")
        return {}

    entries = {}
    for key, entry in bibdata.entries.items():
        doi = entry.fields.get('doi', '').strip()
        eprint = entry.fields.get('eprint', '').strip()
        year = entry.fields.get('year', '')

        entries[key] = {
            'doi': doi if doi else None,
            'arxiv_id': eprint if eprint else None,
            'year': year,
        }

    return entries


def main():
    # Find the project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Load selected publications config
    yaml_path = project_root / 'content' / 'selected-publications.yml'
    if not yaml_path.exists():
        print(f"Error: {yaml_path} not found")
        return

    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)

    # Get BibTeX file path
    bibtex_file = config.get('bibtex_file', '')
    if not os.path.isabs(bibtex_file):
        bibtex_path = yaml_path.parent / bibtex_file
    else:
        bibtex_path = Path(bibtex_file)

    if not bibtex_path.exists():
        print(f"Error: BibTeX file {bibtex_path} not found")
        return

    # Load BibTeX entries
    print(f"Loading BibTeX from {bibtex_path}...")
    bibtex_entries = load_bibtex_entries(str(bibtex_path))

    # Get all publication keys from categories
    pub_keys = set()
    for cat in config.get('categories', []):
        for key in cat.get('publications', []):
            pub_keys.add(key)

    print(f"Found {len(pub_keys)} publications to fetch citations for...")

    # Load manual citation overrides (these take precedence)
    manual_path = project_root / 'content' / 'citations-manual.json'
    manual_citations = {}
    if manual_path.exists():
        with open(manual_path, 'r') as f:
            manual_citations = json.load(f)
        # Remove comment keys
        manual_citations = {k: v for k, v in manual_citations.items() if not k.startswith('_')}
        if manual_citations:
            print(f"Loaded {len(manual_citations)} manual citation overrides")

    # Load existing citations cache
    citations_path = project_root / 'content' / 'citations.json'
    existing_citations = {}
    if citations_path.exists():
        with open(citations_path, 'r') as f:
            existing_citations = json.load(f)
        print(f"Loaded {len(existing_citations)} existing citations from cache")

    # Fetch citations for each publication
    citations = {}
    for i, key in enumerate(sorted(pub_keys)):
        # Skip if we have a manual override
        if key in manual_citations:
            citations[key] = manual_citations[key]
            print(f"  [{i+1}/{len(pub_keys)}] {key}: using manual override ({manual_citations[key].get('cited_by_count', 0)} citations)")
            continue

        if key not in bibtex_entries:
            print(f"  [{i+1}/{len(pub_keys)}] {key}: not in BibTeX")
            continue

        entry = bibtex_entries[key]
        doi = entry.get('doi')
        arxiv_id = entry.get('arxiv_id')

        print(f"  [{i+1}/{len(pub_keys)}] {key}...", end=" ")

        result = fetch_citation_count(doi=doi, arxiv_id=arxiv_id)

        if result:
            citation_entry = {
                'cited_by_count': result['cited_by_count'],
                'year': entry.get('year', ''),
            }
            # Store the appropriate ID based on source
            if result.get('source') == 'openalex':
                citation_entry['openalex_id'] = result.get('openalex_id', '')
                print(f"{result['cited_by_count']} citations (OpenAlex)")
            elif result.get('source') == 'semantic_scholar':
                citation_entry['semantic_scholar_id'] = result.get('semantic_scholar_id', '')
                print(f"{result['cited_by_count']} citations (Semantic Scholar)")
            else:
                print(f"{result['cited_by_count']} citations")
            citations[key] = citation_entry
        else:
            # Keep existing data if we have it
            if key in existing_citations:
                citations[key] = existing_citations[key]
                print(f"using cached: {existing_citations[key].get('cited_by_count', 0)} citations")
            else:
                citations[key] = {
                    'cited_by_count': 0,
                    'year': entry.get('year', ''),
                }
                print("no data")

        # Be polite to the API
        time.sleep(0.1)

    # Save citations
    with open(citations_path, 'w') as f:
        json.dump(citations, f, indent=2, sort_keys=True)

    print(f"\nSaved {len(citations)} citations to {citations_path}")
    if manual_citations:
        print(f"  ({len(manual_citations)} from manual overrides)")

    # Print summary
    total_citations = sum(c.get('cited_by_count', 0) for c in citations.values())
    print(f"Total citations across selected publications: {total_citations:,}")


if __name__ == '__main__':
    main()
