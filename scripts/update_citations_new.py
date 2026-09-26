#!/usr/bin/env python
"""
Fetch citation counts for NEW publications only (not already in citations.json).

Usage:
    python scripts/update_citations_new.py

This is an incremental version of update_citations.py that only fetches
citations for entries that don't already exist in content/citations.json.
Useful when adding new publications without re-fetching everything.
"""

import json
import os
import time
import urllib.request
from pathlib import Path

import yaml

# OpenAlex API endpoint
OPENALEX_API = "https://api.openalex.org/works"

# Be polite - identify ourselves
USER_AGENT = "TheoryAndPractice/1.0 (https://theoryandpractice.org; mailto:kyle.cranmer@wisc.edu)"


def fetch_from_openalex(doi=None, arxiv_id=None):
    """Fetch citation count from OpenAlex for a given DOI or arXiv ID.

    OpenAlex has no `arxiv:` prefix on the works endpoint -- that 404s. arXiv
    preprints are indexed under their DataCite DOI (10.48550/arXiv.<id>), so
    that is what we look up for entries that have no journal DOI.
    """
    urls = []
    if doi:
        urls.append(f"{OPENALEX_API}/doi:{doi}")
    if arxiv_id:
        clean_arxiv = arxiv_id.replace('arXiv:', '').strip()
        urls.append(f"{OPENALEX_API}/doi:10.48550/arXiv.{clean_arxiv}")

    for url in urls:
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
            continue
        except Exception:
            continue

    return None


# Semantic Scholar API endpoint
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper"


# Unauthenticated Semantic Scholar requests share a small rate-limit pool and
# return 429 frequently, so retry with a widening delay before giving up.
S2_RETRIES = 3
S2_BACKOFF = 3


def fetch_from_semantic_scholar(doi=None, arxiv_id=None):
    """Fetch citation count from Semantic Scholar."""
    if doi:
        url = f"{SEMANTIC_SCHOLAR_API}/DOI:{doi}?fields=citationCount,externalIds"
    elif arxiv_id:
        clean_arxiv = arxiv_id.replace('arXiv:', '').strip()
        url = f"{SEMANTIC_SCHOLAR_API}/ARXIV:{clean_arxiv}?fields=citationCount,externalIds"
    else:
        return None

    for attempt in range(S2_RETRIES):
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', USER_AGENT)

            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                paper_id = data.get('paperId', '')
                return {
                    'cited_by_count': data.get('citationCount', 0),
                    'semantic_scholar_id': f"https://www.semanticscholar.org/paper/{paper_id}" if paper_id else '',
                    'source': 'semantic_scholar',
                }
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < S2_RETRIES - 1:
                time.sleep(S2_BACKOFF * (attempt + 1))
                continue
            return None
        except Exception:
            return None

    return None


# INSPIRE-HEP API endpoint. Best coverage for high-energy physics, where both
# OpenAlex and Semantic Scholar undercount badly, and it is not rate-limited.
INSPIRE_API = "https://inspirehep.net/api"


def fetch_from_inspire(doi=None, arxiv_id=None):
    """Fetch citation count from INSPIRE-HEP."""
    urls = []
    if arxiv_id:
        clean_arxiv = arxiv_id.replace('arXiv:', '').strip()
        urls.append(f"{INSPIRE_API}/arxiv/{clean_arxiv}")
    if doi:
        urls.append(f"{INSPIRE_API}/doi/{doi}")

    for url in urls:
        try:
            req = urllib.request.Request(url)
            req.add_header('User-Agent', USER_AGENT)

            with urllib.request.urlopen(req, timeout=15) as response:
                metadata = json.loads(response.read().decode('utf-8')).get('metadata', {})

            recid = metadata.get('control_number')
            return {
                'cited_by_count': metadata.get('citation_count', 0) or 0,
                'inspire_id': f"https://inspirehep.net/literature/{recid}" if recid else '',
                'source': 'inspire',
            }
        except urllib.error.HTTPError:
            continue
        except Exception:
            continue

    return None


def fetch_citation_count(doi=None, arxiv_id=None):
    """Fetch the best citation count available across sources.

    The three sources disagree substantially and none dominates:

      * INSPIRE-HEP has the best coverage for high-energy physics and is not
        rate-limited, but does not index most of the ML/CS venues.
      * OpenAlex often holds only the arXiv *preprint* record for conference
        papers, which badly undercounts them (Learning to Pivot: 88 vs 244).
      * Semantic Scholar merges preprint and published versions, but is
        aggressively rate-limited without an API key and often returns nothing.

    So query all three and keep the larger count rather than taking whichever
    responds first. A citation count that is too low is just as wrong as a
    missing one, and picking the max degrades gracefully when a source fails.
    """
    results = [
        fetch_from_inspire(doi=doi, arxiv_id=arxiv_id),
        fetch_from_openalex(doi=doi, arxiv_id=arxiv_id),
        fetch_from_semantic_scholar(doi=doi, arxiv_id=arxiv_id),
    ]
    results = [r for r in results if r]
    if not results:
        return None

    return max(results, key=lambda r: r.get('cited_by_count', 0))


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

    # Load manual citation overrides (these take precedence)
    manual_path = project_root / 'content' / 'citations-manual.json'
    manual_citations = {}
    if manual_path.exists():
        with open(manual_path, 'r') as f:
            manual_citations = json.load(f)
        # Remove comment keys
        manual_citations = {k: v for k, v in manual_citations.items() if not k.startswith('_')}

    # Load existing citations cache
    citations_path = project_root / 'content' / 'citations.json'
    existing_citations = {}
    if citations_path.exists():
        with open(citations_path, 'r') as f:
            existing_citations = json.load(f)
        print(f"Loaded {len(existing_citations)} existing citations from cache")

    # Find NEW entries (not in cache and not in manual overrides)
    new_keys = []
    for key in sorted(pub_keys):
        if key not in existing_citations and key not in manual_citations:
            new_keys.append(key)

    if not new_keys:
        print("\nNo new publications to fetch citations for.")
        print(f"All {len(pub_keys)} publications already have citation data.")
        return

    print(f"\nFound {len(new_keys)} NEW publications to fetch citations for...")

    # Start with existing citations
    citations = existing_citations.copy()

    # Add manual overrides
    for key in manual_citations:
        citations[key] = manual_citations[key]

    # Fetch citations only for new publications
    fetched = 0
    for i, key in enumerate(new_keys):
        if key not in bibtex_entries:
            print(f"  [{i+1}/{len(new_keys)}] {key}: not in BibTeX")
            continue

        entry = bibtex_entries[key]
        doi = entry.get('doi')
        arxiv_id = entry.get('arxiv_id')

        print(f"  [{i+1}/{len(new_keys)}] {key}...", end=" ")

        result = fetch_citation_count(doi=doi, arxiv_id=arxiv_id)

        if result:
            citation_entry = {
                'cited_by_count': result['cited_by_count'],
                'year': entry.get('year', ''),
            }
            # Store the appropriate ID based on source
            if result.get('source') == 'inspire':
                citation_entry['inspire_id'] = result.get('inspire_id', '')
                print(f"{result['cited_by_count']} citations (INSPIRE)")
            elif result.get('source') == 'openalex':
                citation_entry['openalex_id'] = result.get('openalex_id', '')
                print(f"{result['cited_by_count']} citations (OpenAlex)")
            elif result.get('source') == 'semantic_scholar':
                citation_entry['semantic_scholar_id'] = result.get('semantic_scholar_id', '')
                print(f"{result['cited_by_count']} citations (Semantic Scholar)")
            else:
                print(f"{result['cited_by_count']} citations")
            citations[key] = citation_entry
            fetched += 1
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

    print(f"\nFetched {fetched} new citations")
    print(f"Saved {len(citations)} total citations to {citations_path}")

    # Print summary
    total_citations = sum(c.get('cited_by_count', 0) for c in citations.values())
    print(f"Total citations across selected publications: {total_citations:,}")


if __name__ == '__main__':
    main()
