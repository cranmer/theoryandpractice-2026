#!/usr/bin/env python
"""Pelican configuration for Theory And Practice site."""

# Patch nbconvert to use 'basic' template instead of 'lab' to avoid CSS conflicts
# The 'lab' template injects massive JupyterLab CSS that breaks Bootstrap styling
from nbconvert.exporters import HTMLExporter
_original_init = HTMLExporter.__init__
def _patched_init(self, *args, **kwargs):
    if 'template_name' not in kwargs:
        kwargs['template_name'] = 'basic'
    _original_init(self, *args, **kwargs)
HTMLExporter.__init__ = _patched_init

AUTHOR = 'Kyle Cranmer'
SITENAME = 'Theory And Practice'
SITEURL = ''
PATH = 'content'

TIMEZONE = 'America/Chicago'
DEFAULT_LANG = 'en'

# Feed generation (disabled during development)
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Menu configuration
DISPLAY_PAGES_ON_MENU = False
MENUITEMS = (
    ('Research', '/pages/Research.html'),
    ('Projects', '/pages/projects.html'),
    ('Talks', '/presentations.html'),
    ('Publications', '/publications.html'),
    ('Media & Outreach', '/pages/in-the-news.html'),
)

# Links
LINKS = (
    ('Data Science Institute', 'https://dsi.wisc.edu'),
    ('My UW Physics webpage', 'https://www.physics.wisc.edu/directory/cranmer-kyle/'),
    ('IRIS-HEP', 'https://iris-hep.org/'),
    ('wikipedia', 'https://en.wikipedia.org/wiki/Kyle_Cranmer')
)

# Social
SOCIAL = (
    ('Bluesky', 'https://bsky.app/profile/kylecranmer.bsky.social', 'bluesky'),
    ('twitter', 'http://twitter.com/kylecranmer'),
    ('instagram', 'https://www.instagram.com/kyle.cranmer/'),
    ('github', 'http://github.com/cranmer'),
    ('linkedin', 'http://www.linkedin.com/in/kylecranmer'),
    ('youtube', 'https://www.youtube.com/channel/UCKl2VoIJiPYp3QhuK22b7xQ'),
    ('INSPIRE (≤ 10 authors)', 'https://inspirehep.net/literature?sort=mostrecent&size=25&page=1&q=a%3Ak.s.cranmer.1%20and%20ac%201-%3E10&ui-citation-summary=true', 'inspire'),
    ('Google Scholar', 'http://scholar.google.com/citations?user=EZjSxgwAAAAJ', 'google-scholar'),
    ('ORCiD', 'https://orcid.org/0000-0002-5769-7094', 'orcid'),
)

CC_LICENSE = "CC-BY-NC"
DEFAULT_PAGINATION = 6

# URL structure (maintain compatibility with old site)
ARTICLE_URL = '{date:%Y}/{date:%m}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{slug}/index.html'

# Static paths
STATIC_PATHS = [
    'images',
    'downloads',
    'downloads/notebooks',
    'downloads/files',
    'downloads/code',
    'favicon.png',
    'extra/CNAME',
    'css',
    'js',
]
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'}}

# Don't process HTML files as content
READERS = {'html': None}

# Code and notebook directories
CODE_DIR = 'downloads/code'
# NOTEBOOK_DIR must be empty because the paths in content already include full path
NOTEBOOK_DIR = ''

# Publications (pelican-bibtex)
PUBLICATIONS_SRC = 'content/cranmer-2025-lt20authors.bib'

# Plugin configuration
PLUGIN_PATHS = ['plugins']
PLUGINS = [
    # Namespace plugins (auto-discovered via pip install)
    'render_math',
    'sitemap',
    'neighbors',
    'liquid_tags',
    'pelican_presentations',
    # Local plugins
    'i18n_init',  # Minimal i18n for theme (replaces pelican-i18n-subsites)
    'pelican_javascript',
    'pelican-cite',
    'pelican-bibtex',
]

# Liquid tags configuration - enable specific tags
LIQUID_TAGS = ['img', 'video', 'youtube', 'include_code', 'literal', 'notebook']

# Jupyter notebook support via pelican-jupyter
MARKUP = ('md', 'ipynb')
IPYNB_MARKUP_USE_FIRST_CELL = True
IGNORE_FILES = ['.ipynb_checkpoints']

# Theme configuration
THEME = 'themes/pelican-bootstrap3'
JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}

# Bootstrap theme (from Bootswatch)
BOOTSTRAP_THEME = 'flatly'

# Bootstrap3 theme settings
DISPLAY_BREADCRUMBS = False
BOOTSTRAP_NAVBAR_INVERSE = False
DISPLAY_RECENT_POSTS_ON_SIDEBAR = True

# Tag cloud
TAG_CLOUD_STEPS = 4
TAG_CLOUD_BADGE = True
DISPLAY_TAGS_ON_SIDEBAR = True
TAG_CLOUD_MAX_ITEMS = 25
DISPLAY_TAGS_INLINE = True
HIDE_SIDEBAR = False

# About section (disabled)
AVATAR = None
ABOUT_ME = None

# Social sharing
ADDTHIS_PROFILE = 'ra-5332e76b5340f5f3'

# Open Graph and Twitter Cards for social media previews
TWITTER_CARDS = True
TWITTER_USERNAME = 'kylecranmer'
OPEN_GRAPH_IMAGE = 'images/Kyle-Cranmer-headshot-cropped-square-web.jpeg'

# Analytics
GOOGLE_ANALYTICS = 'UA-3337202-1'

# Pygments code highlighting
PYGMENTS_STYLE = 'default'

# Markdown configuration - enable md_in_html for markdown inside HTML blocks
MARKDOWN = {
    'extension_configs': {
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
        'markdown.extensions.md_in_html': {},
    },
    'output_format': 'html5',
}

# Direct templates (for publications, presentations, and search pages)
DIRECT_TEMPLATES = ['index', 'categories', 'authors', 'archives', 'publications', 'presentations', 'search']

# Presentations (pelican-presentations plugin)
PRESENTATIONS_SRC = 'content/presentations.yml'

# Sitemap configuration
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}
