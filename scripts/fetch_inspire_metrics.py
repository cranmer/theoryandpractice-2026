#!/usr/bin/env python3
"""Fetch publication/citation/h-index metrics used by the publications page.

The two metrics boxes on the publications page come from different sources:

  * "All publications"          - publication count from INSPIRE, but citations
                                  and h-index from Google Scholar (INSPIRE's
                                  citation totals run well below Scholar's).
  * "Publications with <20 authors" - entirely from INSPIRE.

This script only covers the INSPIRE half, which is the part that can be
fetched reliably. Google Scholar has no API and blocks scraping, so the
Scholar citations/h-index still have to be read off the profile by hand:

    https://scholar.google.com/citations?user=EZjSxgwAAAAJ

Usage:
    python scripts/fetch_inspire_metrics.py

Results are printed for manual transfer into the metrics dicts in
pelicanconf.py. Nothing is written automatically -- the values are rounded
and reviewed before they go on the site.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://inspirehep.net/api/literature"

# INSPIRE author identifier for Kyle Cranmer (record 1012846).
AUTHOR = "k.s.cranmer.1"

# `ac 1->19` is the "fewer than 20 authors" cut shown on the publications page.
QUERIES = [
    ("All publications", f"a {AUTHOR}"),
    ("Publications with <20 authors", f"a {AUTHOR} and ac 1->19"),
]

PAGE_SIZE = 1000


def fetch_counts(query):
    """Return (total_records, [citation_count, ...]) for an INSPIRE query."""
    counts = []
    total = None
    page = 1

    while True:
        params = urllib.parse.urlencode({
            "q": query,
            "fields": "citation_count",
            "size": PAGE_SIZE,
            "page": page,
            "sort": "mostrecent",
        })
        request = urllib.request.Request(
            f"{API}?{params}",
            headers={"User-Agent": "theoryandpractice-site/1.0"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            hits = json.load(response)["hits"]

        if total is None:
            total = hits["total"]

        batch = hits["hits"]
        if not batch:
            break

        counts.extend(
            hit.get("metadata", {}).get("citation_count", 0) or 0 for hit in batch
        )
        if len(counts) >= total:
            break

        page += 1
        time.sleep(1)  # be polite to the INSPIRE API

    return total, counts


def h_index(counts):
    """Largest h such that h papers each have at least h citations."""
    h = 0
    for rank, citations in enumerate(sorted(counts, reverse=True), start=1):
        if citations < rank:
            break
        h = rank
    return h


def main():
    for label, query in QUERIES:
        try:
            total, counts = fetch_counts(query)
        except urllib.error.URLError as exc:
            print(f"{label}: FAILED ({exc})")
            continue

        print(f"{label}")
        print(f"  query              = {query}")
        print(f"  total_publications = {total} (retrieved {len(counts)})")
        print(f"  total_citations    = {sum(counts):,}")
        print(f"  h_index            = {h_index(counts)}")
        print()

    print("Google Scholar (manual, no API):")
    print("  https://scholar.google.com/citations?user=EZjSxgwAAAAJ")
    print("  Read 'Citations (All)' and 'h-index (All)' for the all-publications box.")


if __name__ == "__main__":
    main()
