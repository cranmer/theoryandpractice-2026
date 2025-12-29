"""
Pelican Selected Publications Plugin
====================================

Generates a selected publications page organized by thematic categories.

Configuration:
    SELECTED_PUBLICATIONS_SRC: Path to YAML file with category definitions

YAML format:
    bibtex_file: "path/to/publications.bib"
    categories:
      - id: category-id
        title: "Category Title"
        description: "Category description"
        publications:
          - BibtexKey1
          - BibtexKey2
    highlights:
      - BibtexKey1  # Optional: mark specific papers as highlights
"""

import logging
import os
import re

from pelican import signals

logger = logging.getLogger(__name__)

try:
    from io import StringIO
    from pybtex.database.input.bibtex import Parser
    from pybtex.database.output.bibtex import Writer
    from pybtex.database import BibliographyData
    from pybtex.backends import html
    from pybtex.style.formatting import plain
    PYBTEX_AVAILABLE = True
except ImportError:
    PYBTEX_AVAILABLE = False
    logger.warning('pelican-selected-publications: pybtex not available')

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logger.warning('pelican-selected-publications: PyYAML not available')


def format_publication(entry, key, plain_style, html_backend):
    """Format a single BibTeX entry to HTML."""
    # Workaround for entries missing certain fields
    if 'journal' not in entry.fields:
        entry.fields['journal'] = ''
    if 'booktitle' not in entry.fields:
        entry.fields['booktitle'] = ''

    # Format using pybtex
    bibdata = BibliographyData(entries={key: entry})
    formatted = list(plain_style.format_entries(bibdata.entries.values()))[0]
    text = formatted.text.render(html_backend)

    # Clean up formatting artifacts
    text = text.replace('\\{', '&#123;')
    text = text.replace('\\}', '&#125;')
    text = text.replace('{', '')
    text = text.replace('}', '')

    # Replace the title's bibtex-protected span with pub-title class
    # Get the title from the entry and find its span
    title = entry.fields.get('title', '')
    # Clean title for matching (remove braces)
    clean_title = title.replace('{', '').replace('}', '')
    if clean_title:
        # Escape special regex characters in title
        escaped_title = re.escape(clean_title)
        # Replace the span containing the title with pub-title class
        pattern = r'<span class="bibtex-protected">' + escaped_title + r'</span>'
        replacement = r'<span class="pub-title">' + clean_title + r'</span>'
        text = re.sub(pattern, replacement, text, count=1)

    # Generate BibTeX string
    bib_buf = StringIO()
    Writer().write_stream(bibdata, bib_buf)
    bibtex = bib_buf.getvalue()

    # Extract useful fields
    year = entry.fields.get('year', '')
    doi = entry.fields.get('doi', '')
    eprint = entry.fields.get('eprint', '')
    url = entry.fields.get('url', '')
    pdf = entry.fields.get('pdf', '')

    return {
        'key': key,
        'text': text,
        'bibtex': bibtex,
        'year': year,
        'doi': doi,
        'eprint': eprint,
        'url': url,
        'pdf': pdf,
    }


def add_selected_publications(generator):
    """
    Populates context with selected publications organized by category.

    Output:
        generator.context['selected_publications']: dict with:
            - categories: list of category dicts, each containing:
                - id: category identifier
                - title: display title
                - description: category description
                - publications: list of formatted publication dicts
            - highlights: set of keys marked as highlights
    """
    if not PYBTEX_AVAILABLE:
        logger.warning('pelican-selected-publications: pybtex required')
        return

    if not YAML_AVAILABLE:
        logger.warning('pelican-selected-publications: PyYAML required')
        return

    yaml_path = generator.settings.get('SELECTED_PUBLICATIONS_SRC')
    if not yaml_path:
        return

    # Load YAML configuration
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f'pelican-selected-publications: failed to load {yaml_path}: {e}')
        return

    # Get BibTeX file path (relative to YAML or absolute)
    bibtex_file = config.get('bibtex_file', '')
    if not os.path.isabs(bibtex_file):
        bibtex_file = os.path.join(os.path.dirname(yaml_path), bibtex_file)

    # Parse BibTeX
    try:
        bibdata = Parser().parse_file(bibtex_file)
    except Exception as e:
        logger.error(f'pelican-selected-publications: failed to parse {bibtex_file}: {e}')
        return

    # Initialize pybtex formatting
    plain_style = plain.Style()
    html_backend = html.Backend()

    # Get highlights set
    highlights = set(config.get('highlights', []))

    # Process categories
    categories = []
    for cat_config in config.get('categories', []):
        cat_id = cat_config.get('id', '')
        cat_title = cat_config.get('title', '')
        cat_desc = cat_config.get('description', '')
        pub_keys = cat_config.get('publications', [])

        publications = []
        for key in pub_keys:
            if key not in bibdata.entries:
                logger.warning(f'pelican-selected-publications: key "{key}" not found in BibTeX')
                continue

            entry = bibdata.entries[key]
            pub = format_publication(entry, key, plain_style, html_backend)
            pub['highlight'] = key in highlights
            publications.append(pub)

        categories.append({
            'id': cat_id,
            'title': cat_title,
            'description': cat_desc,
            'publications': publications,
        })

    # Add to context
    generator.context['selected_publications'] = {
        'categories': categories,
        'highlights': highlights,
    }

    logger.info(f'pelican-selected-publications: loaded {sum(len(c["publications"]) for c in categories)} publications in {len(categories)} categories')


def register():
    signals.generator_init.connect(add_selected_publications)
