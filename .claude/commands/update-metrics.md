# Update Citation Metrics

Refresh the two publication metrics boxes shown at the top of the publications page.

## File to edit
`pelicanconf.py` — the `PUBLICATION_METRICS`, `ALL_PUBLICATION_METRICS`, and
`SMALL_AUTHOR_METRICS` dicts (all three live together, under a comment recording
the sources and the date of the last refresh).

## Where the numbers come from
The two boxes use **different sources**. Do not mix them up — INSPIRE's citation
totals run well below Google Scholar's, so swapping sources silently makes the
numbers look like a sudden drop.

| Box | Publications | Citations & h-index |
|---|---|---|
| "All publications" | INSPIRE, `a k.s.cranmer.1` | **Google Scholar** profile `EZjSxgwAAAAJ` |
| "Publications with <20 authors" | INSPIRE, `a k.s.cranmer.1 and ac 1->19` | same INSPIRE query |

`PUBLICATION_METRICS` is a backwards-compatibility duplicate of
`ALL_PUBLICATION_METRICS` (the homepage needs it) — update both to the same values.

## Instructions
1. Run the INSPIRE half:
   ```
   python scripts/fetch_inspire_metrics.py
   ```
   It prints publication count, total citations, and h-index for both queries.
   It writes nothing — the values are reviewed before they go on the site.

2. Get the Google Scholar citations and h-index. There is no Scholar API and
   scraping is blocked, so fetch the profile page and read
   "Citations (All)" and "h-index (All)":
   ```
   https://scholar.google.com/citations?user=EZjSxgwAAAAJ
   ```

3. Update the three dicts in `pelicanconf.py`:
   - `ALL_PUBLICATION_METRICS` and `PUBLICATION_METRICS`: INSPIRE publication
     count, Scholar citations, Scholar h-index.
   - `SMALL_AUTHOR_METRICS`: all three from the `ac 1->19` INSPIRE query.

4. **Round the citation totals** (e.g. 374,265 → 374,000; 15,859 → 15,900).
   Publication counts and h-index are left exact. Exact citation figures imply a
   precision that goes stale within days.

5. Update the `last refreshed` date in the comment above the dicts, and correct
   the recorded source values if they have changed.

6. Verify: if the dev server is running, wait for the rebuild and check the
   rendered values; otherwise rebuild with
   `pixi run pelican content -s pelicanconf.py`.

## Per-paper citation counts
The counts shown next to each individual publication are separate from the
boxes above — they live in `content/citations.json`. Refresh them with:

```
pixi run update-citations          # all selected publications
pixi run update-citations-new      # only keys not already in citations.json
```

The script queries **three** sources and keeps the **larger** count, because
none of them dominates:

- **INSPIRE-HEP** — best coverage for high-energy physics (often several times
  what the others report) and not rate-limited, but doesn't index most ML/CS
  venues.
- **OpenAlex** — frequently holds only the arXiv preprint record for conference
  papers and undercounts them badly (Learning to Pivot: 88 vs 244). Note there
  is no `arxiv:` prefix on its works endpoint; arXiv papers are looked up via
  their DataCite DOI, `10.48550/arXiv.<id>`.
- **Semantic Scholar** — merges preprint and published versions, but is heavily
  rate-limited without an API key and often returns nothing.

The citation link next to each paper points at whichever source supplied the
number (`inspire_id` / `openalex_id` / `semantic_scholar_id` in citations.json).
The script also never lowers an existing cached count. After running, check that
no counts went *down* — that means a source lost coverage, not that citations
disappeared.

`content/citations-manual.json` holds overrides that take precedence over all
fetched data; use it for papers the APIs can't resolve.

Note: changes to the plugin in `plugins/pelican-selected-publications/` are
**not** picked up by `--autoreload`, which watches only content, theme, and
settings. Restart the dev server after editing it.

## Notes
- Report the before/after numbers so the change can be sanity-checked. A metric
  moving *down* usually means a source got swapped, not that citations vanished.
- Don't invent a publication count for the all-publications box. If INSPIRE is
  unreachable, leave the existing count rather than substituting another source.

## User input
$ARGUMENTS
