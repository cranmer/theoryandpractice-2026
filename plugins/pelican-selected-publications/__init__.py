"""
Pelican Selected Publications
=============================

A Pelican plugin that generates a selected publications page organized
by thematic categories. Categories and publication assignments are
defined in a YAML file, while bibliographic data comes from BibTeX.
"""

from .selected_publications import register

__version__ = '1.0.0'
