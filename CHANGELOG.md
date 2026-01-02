# Changelog

All notable changes to theoryandpractice.org are documented in this file.

## [2026-01-02] - Media & Outreach Plugin

### Added
- **New** Media & Outreach page (`/media.html`) with embedded videos, podcasts, and articles
  - Custom `pelican-media` plugin for YAML-driven media organization
  - Card and list view toggle (matching projects and collaborators pages)
  - Category filtering (Videos, Podcasts, Articles, Interviews, Outreach)
  - Year filtering
  - Embedded YouTube and Vimeo video players
  - Featured items highlighted with star badge
  - Responsive grid layout
- **New** `search_media.py` helper script to find new media mentions via Google News RSS
  - Run with `pixi run search-media`
  - Supports SerpAPI for enhanced results (optional)
  - Outputs YAML suggestions for easy addition to `media.yml`

### Changed
- Navigation "Media & Outreach" now links to new `/media.html` (was `/pages/in-the-news.html`)
- Migrated all media items from static markdown page to structured YAML

### Theme
- Added `media.html` template with card grid and list view styles

## [2025-12-31] - Collaborators List View

### Added
- Card/list view toggle for collaborators page (matching projects page)

## [2025-12-29] - CV and Publications Enhancements

### Added
- **CV page** (`/pages/cv.html`) with bio, experience, education, awards, and highlights
- **Selected Publications page** (`/selected-publications.html`) with thematic categories
  - `pelican-selected-publications` plugin for YAML-driven publication organization
  - Filter by category, year, and highlighted papers
  - Publication metrics section (total papers, citations, h-index)
  - Profile icons: Google Scholar, INSPIRE, arXiv, OpenAlex, ORCiD
  - Official arXiv logomark icon
  - Collapsible Altmetric badges for each publication
  - Global "Show altmetrics" toggle to expand all badges
  - BibTeX modal with copy-to-clipboard
- Bio section at top of CV page
- Custom navbar hover color (#EE9F43 orange)

### Changed
- Publications menu item now links to Selected Publications page
- Removed "Research" from navigation (content moved to CV bio)
- Publication titles styled in teal (#18bc9c)
- Category headings use h4 for better hierarchy

### Theme
- Added `selected-publications.html` template
- Added section divider styling (teal, 50% width)
- Added Altmetric embed integration
- Added custom icons for arXiv and OpenAlex

## [2025-12-27] - Migration Complete

### Added
- Fresh repository migrated from Pelican 3.7 to Pelican 4.11
- pixi environment management for reproducible builds
- GitHub Actions deployment workflow to cranmer.github.io
- Publications page (`/publications.html`) generated from BibTeX
- Presentations page (`/presentations.html`) with 113 talks from IRIS-HEP format YAML
- Video camera icons for presentations with recordings
- `pelican-presentations` plugin (separate repository) for IRIS-HEP compatible presentations
- Pagefind search (`/search.html`) with instant client-side search across all pages
- Search icon (magnifying glass) in navbar
- Bluesky social link with custom butterfly icon
- Custom SVG icons for Google Scholar, ORCiD, and INSPIRE-HEP
- Instagram social link
- Open Graph and Twitter Card meta tags for social media preview cards
- Theory & Practice logo for social media previews
- BibTeX modal popups with copy-to-clipboard functionality
- Markdown rendering inside HTML blocks (`md_in_html` extension)
- Custom `pelican-cite.css` stylesheet placeholder
- Comprehensive README documentation
- This CHANGELOG file

### Changed
- License updated from CC-BY to CC-BY-NC (non-commercial)
- Plugin architecture modernized to use namespace plugins where available
- Local plugins (`pelican-cite`, `pelican-bibtex`, `pelican_javascript`) retained with modifications
- Theme template modifications for custom CSS/JS per page
- `.gitignore` updated to only ignore root `/src/` directory (not plugin src directories)

### Fixed
- Markdown links not rendering inside HTML `<div>` blocks (Home.md)
- Floating images appearing in blog index summaries (added explicit Summary metadata)
- BibTeX popup windows blocked by modern browsers (replaced with Bootstrap modals)
- Missing `extra_stylesheets` block in theme templates
- Navigation showing stale category entries (fixed serve task to clean before build)

### Plugins

#### pelican-cite
- Added Bootstrap modal for viewing BibTeX entries
- Added copy-to-clipboard button
- BibTeX link appears before back-reference arrow
- Proper newline formatting in BibTeX display

#### pelican-bibtex
- Added Bootstrap modal (replacing `window.open` popups)
- Added copy-to-clipboard functionality
- URL-encoded BibTeX content for reliable display

#### pelican_javascript
- Migrated to Pelican 4 signal API
- Supports both articles and pages

### Theme (pelican-bootstrap3)
- Added `extra_stylesheets` block to `base.html`
- Added stylesheet/javascript rendering to `article.html` and `page.html`
- Added `publications.html` template
- Added `presentations.html` template with video icon support
- Added Bluesky to social icon whitelist
- Added custom CSS for Bluesky butterfly icon (SVG-based)
- Added custom SVG icons for Google Scholar, ORCiD, and INSPIRE-HEP (Font Awesome 4.x lacks these)

## [Pre-Migration] - Original TheoryAndPractice

The original site was maintained at https://github.com/cranmer/TheoryAndPractice using:
- Pelican 3.7.1
- Various pelican-plugins as git submodules
- Manual deployment process

See the original repository for historical changes.
