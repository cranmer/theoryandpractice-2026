# pelican-selected-publications

A Pelican plugin that generates a curated publications page organized by research themes, with citation counts, filtering, sorting, and Altmetric integration.

## Features

- **YAML-driven organization**: Define publication categories with BibTeX keys
- **Filtering**: Filter by category, year, or highlighted papers
- **Sorting**: Sort by category, date, or citation count (toggle buttons)
- **Citation counts**: Automatic fetching from OpenAlex and Semantic Scholar APIs
- **Aggregate metrics**: Display total publications, citations, and h-index
- **Profile links**: Icons linking to Google Scholar, INSPIRE, arXiv, OpenAlex, ORCiD
- **Altmetric badges**: Collapsible Altmetric donut badges for each publication
- **BibTeX modal**: Click to view/copy BibTeX entries

## Installation

1. Copy the `pelican-selected-publications` directory to your `plugins/` folder
2. Add to your `pelicanconf.py`:

```python
PLUGIN_PATHS = ['plugins']
PLUGINS = [
    # ... other plugins
    'pelican-selected-publications',
]
```

## Configuration

### Required Settings

```python
# Path to YAML file defining categories and publications
SELECTED_PUBLICATIONS_SRC = 'content/selected-publications.yml'
```

### Optional Settings

```python
# Aggregate metrics for all publications (e.g., from Google Scholar)
ALL_PUBLICATION_METRICS = {
    'total_publications': 1200,
    'total_citations': 349000,
    'h_index': 241,
}

# Metrics for publications with fewer authors (e.g., excluding large collaborations)
SMALL_AUTHOR_METRICS = {
    'total_publications': 119,
    'total_citations': 14000,
    'h_index': 41,
}

# Profile links displayed as icons
PUBLICATION_PROFILES = (
    ('Google Scholar', 'http://scholar.google.com/citations?user=...', 'google-scholar'),
    ('INSPIRE', 'https://inspirehep.net/authors/...', 'inspire'),
    ('arXiv', 'https://arxiv.org/search/?searchtype=author&query=...', 'arxiv'),
    ('OpenAlex', 'https://openalex.org/works?filter=authorships.author.id:...', 'openaccess'),
    ('ORCiD', 'https://orcid.org/0000-0000-0000-0000', 'orcid'),
)
```

## YAML Configuration File

Create a YAML file (e.g., `content/selected-publications.yml`) with the following structure:

```yaml
# Path to BibTeX file (relative to YAML file or absolute)
bibtex_file: "selected-publications.bib"

# Publications to highlight with a star
highlights:
  - Cranmer:2019eaq
  - ATLAS:2012yve

# Categories with publication lists
categories:
  - id: sbi
    title: "Simulation-based Inference Methodology"
    description: "Methods for inference when likelihoods are intractable."
    publications:
      - Cranmer:2019eaq
      - Brehmer:2018hga
      - Brehmer:2018kdj

  - id: higgs
    title: "Higgs Discovery"
    description: "Key papers from the Higgs boson discovery."
    publications:
      - ATLAS:2012yve
      - Cowan:2010js
```

## Citation Counts

The plugin supports automatic citation count fetching from academic APIs.

### Fetching Citations

Run the update script to fetch citation counts:

```bash
pixi run update-citations
# or directly:
python scripts/update_citations.py
```

This will:
1. Read all publication keys from your YAML categories
2. Look up each paper in OpenAlex (primary) and Semantic Scholar (fallback)
3. Save results to `content/citations.json`

### Incremental Updates (New Entries Only)

When adding new publications, use the incremental script to only fetch citations
for entries not already in `citations.json`:

```bash
pixi run update-citations-new
# or directly:
python scripts/update_citations_new.py
```

This is faster and avoids unnecessary API calls when you've just added a few new papers.

### Data Sources (Priority Order)

1. **Manual overrides** (`content/citations-manual.json`) - highest priority
2. **OpenAlex API** - primary source, good coverage of recent papers
3. **Semantic Scholar API** - fallback, often has papers OpenAlex misses
4. **Cached data** - if both APIs fail, keeps previous values
5. **Zero** - last resort for papers with no data anywhere

### Manual Citation Overrides

For papers not found by either API, add manual entries to `content/citations-manual.json`:

```json
{
  "_comment": "Manual citation overrides. Keys starting with _ are ignored.",
  "SomePaper:2020abc": {
    "cited_by_count": 150,
    "openalex_id": "https://openalex.org/W1234567890",
    "year": "2020"
  },
  "AnotherPaper:2019xyz": {
    "cited_by_count": 42,
    "year": "2019"
  }
}
```

Fields:
- `cited_by_count` (required): The citation count to display
- `openalex_id` or `semantic_scholar_id` (optional): URL for the citation link
- `year` (optional): Publication year

### Output Format

The script outputs the source for each paper:

```
[1/68] ATLAS:2012yve... 10301 citations (OpenAlex)
[2/68] Cranmer:2019eaq... 1037 citations (Semantic Scholar)
[3/68] CustomPaper:2020: using manual override (150 citations)
[4/68] OldPaper:2003... using cached: 0 citations
```

## Template

The plugin requires a `selected-publications.html` template in your theme's `templates/` directory. The template receives:

- `selected_publications.categories`: List of category dicts with publications
- `selected_publications.highlights`: Set of highlighted publication keys
- `selected_publications.all_publications`: Flat list of all publications (for sorting)
- `ALL_PUBLICATION_METRICS`: Aggregate metrics dict
- `SMALL_AUTHOR_METRICS`: Small-author metrics dict
- `PUBLICATION_PROFILES`: Tuple of profile links

Each publication dict contains:
- `key`: BibTeX key
- `text`: Formatted HTML citation
- `bibtex`: Raw BibTeX string
- `year`: Publication year
- `doi`: DOI if available
- `eprint`: arXiv ID if available
- `url`: URL if available
- `pdf`: PDF link if available
- `highlight`: Boolean, true if in highlights list
- `citations`: Citation count (integer)
- `citation_url`: Link to OpenAlex or Semantic Scholar entry

## Dependencies

- `pybtex`: BibTeX parsing and formatting
- `PyYAML`: YAML configuration parsing

For citation fetching (optional):
- Python 3.11+ (uses standard library `urllib`)

## License

MIT License
