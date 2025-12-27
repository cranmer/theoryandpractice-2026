# Theory And Practice

Kyle Cranmer's personal website, built with [Pelican](https://getpelican.com/).

**Live site:** [https://theoryandpractice.org](https://theoryandpractice.org)

## Migration from Pelican 3.7 to 4.11

This repository is a fresh migration of the original [TheoryAndPractice](https://github.com/cranmer/TheoryAndPractice) repository, which used Pelican 3.7.1. The migration was performed in December 2025 to modernize the site infrastructure.

### Key Changes in Migration

- **Pelican version**: 3.7.1 → 4.11.0
- **Environment management**: Now uses [pixi](https://pixi.sh/) for reproducible environments
- **Plugin system**: Migrated to Pelican 4's namespace plugin architecture where possible
- **Deployment**: GitHub Actions workflow deploys to [cranmer/cranmer.github.io](https://github.com/cranmer/cranmer.github.io)

### What Was Preserved

- All existing content and URL structure
- pelican-bootstrap3 theme with Bootswatch 'flatly' styling
- Custom per-page JavaScript and CSS functionality
- Jupyter notebook embedding via liquid tags
- BibTeX bibliography support

## Development

### Prerequisites

Install [pixi](https://pixi.sh/):

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

### Local Development

```bash
# Build the site
pixi run build

# Serve locally with auto-rebuild
pixi run serve

# Clean output directory
pixi run clean

# Build for production
pixi run publish
```

The local server runs at http://localhost:8000

## Deployment

The site is deployed automatically via GitHub Actions when pushing to the `main` branch.

### How It Works

1. Push to `main` triggers `.github/workflows/deploy.yml`
2. GitHub Actions builds the site using `publishconf.py`
3. Output is pushed to the `cranmer/cranmer.github.io` repository
4. GitHub Pages serves the site at theoryandpractice.org

### Deploy Key Setup

The workflow uses a deploy key to push to the external repository:
- Generate an SSH key pair
- Add the public key as a deploy key (with write access) to `cranmer/cranmer.github.io`
- Add the private key as a secret named `DEPLOY_KEY` to this repository

## Plugins

### Namespace Plugins (via pip)

These are installed from PyPI and auto-discovered by Pelican:

| Plugin | Purpose |
|--------|---------|
| `pelican-render-math` | LaTeX math rendering |
| `pelican-liquid-tags` | Liquid template tags (notebook embedding, etc.) |
| `pelican-i18n-subsites` | Internationalization support |
| `pelican-neighbors` | Next/previous article navigation |
| `pelican-sitemap` | XML sitemap generation |
| `pelican-jupyter` | Jupyter notebook support |

### Local Plugins (in `plugins/`)

These are custom or modified plugins maintained locally:

#### `pelican_javascript`
Allows per-article/page custom JavaScript and CSS via metadata:
```markdown
JavaScripts: custom.js, https://example.com/lib.js
Stylesheets: custom.css
```

#### `pelican-cite`
Inline BibTeX citations with `[@citation-key]` syntax. Generates a bibliography section at the end of articles.

**Modifications made:**
- Added Bootstrap modal popup for viewing BibTeX entries
- Added "Copy to Clipboard" functionality
- BibTeX entries display with proper formatting

#### `pelican-bibtex`
Generates a publications page from a BibTeX file.

**Modifications made:**
- Bootstrap modal for BibTeX display (replacing broken popup windows)
- Copy to clipboard functionality
- Handles missing `journal` and `booktitle` fields gracefully

## Theme

The site uses [pelican-bootstrap3](https://github.com/getpelican/pelican-themes/tree/master/pelican-bootstrap3) with the Bootswatch 'flatly' theme.

### Theme Modifications

- Added `extra_stylesheets` block for per-page CSS
- Added per-page JavaScript support in article/page templates
- Added Bluesky social icon (custom CSS with SVG, since Font Awesome 4.x lacks it)
- Added `publications.html` template for bibliography page

## Configuration

- `pelicanconf.py` - Development configuration
- `publishconf.py` - Production configuration (extends pelicanconf.py)

### Key Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| `SITEURL` | `https://theoryandpractice.org` | Production URL |
| `THEME` | `themes/pelican-bootstrap3` | Bootstrap 3 theme |
| `BOOTSTRAP_THEME` | `flatly` | Bootswatch theme variant |
| `CC_LICENSE` | `CC-BY-NC` | Creative Commons license |
| `PUBLICATIONS_SRC` | `content/kyle-20authors.bib` | BibTeX file for publications |

## Content Structure

```
content/
├── pages/           # Static pages (Home, Research, Projects, etc.)
├── images/          # Image assets
├── css/             # Custom stylesheets
├── js/              # Custom JavaScript
├── downloads/       # Downloadable files and notebooks
└── *.md             # Blog posts
```

## License

Content is licensed under [Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/).
