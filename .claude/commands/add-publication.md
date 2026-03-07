# Add Publication

Add a new selected publication to the website.

## Input
The user will provide details in natural language — a paper title, arXiv ID, DOI, or URL. Fetch metadata as needed.

## Files to edit
1. `content/selected-publications.bib` — BibTeX entries
2. `content/selected-publications.yml` — Category assignments and highlights

## BibTeX format (`selected-publications.bib`)
Add a standard BibTeX entry. Use INSPIRE-style keys (e.g., `Cranmer:2019eaq`):

```bibtex
@article{AuthorLastName:YYYYxxx,
    author = "Last, First and Last2, First2",
    title = "{Paper Title}",
    eprint = "XXXX.XXXXX",
    archivePrefix = "arXiv",
    primaryClass = "hep-ph",
    doi = "10.xxxx/yyyy",
    journal = "Journal Name",
    volume = "XX",
    pages = "XXX--XXX",
    year = "YYYY"
}
```

## YAML format (`selected-publications.yml`)
Add the BibTeX key to the appropriate category under `publications:`. Existing categories:
- `sbi` — Simulation-based Inference Methodology
- `flows` — Generative Models: Normalizing Flows on Manifolds
- `lattice` — AI-Enhanced Sampling for Lattice Field Theory
- `amplitudes` — AI for Amplitudes
- `statistics` — Statistics Methodology for Particle Physics
- `reinterpretation` — Analysis Reinterpretation & Preservation
- `higgs` — Higgs Boson Discovery & Properties
- `searches` — Beyond Standard Model Searches
- `review` — Review Articles

If the paper doesn't fit existing categories, ask the user or create a new one.

Optionally add to `highlights:` list if it's a landmark paper.

## Instructions
1. Read both files to understand current structure
2. If given an arXiv ID or URL, fetch the paper metadata
3. Add the BibTeX entry to `selected-publications.bib` in the appropriate section
4. Add the key to the right category in `selected-publications.yml`
5. Ask the user if it should be highlighted
6. After editing, rebuild the site with `pixi run pelican content -s pelicanconf.py`

## User input
$ARGUMENTS
