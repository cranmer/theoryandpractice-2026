# Changelog

All notable changes to theoryandpractice.org are documented in this file.

## [2025-12-27] - Migration Complete

### Added
- Fresh repository migrated from Pelican 3.7 to Pelican 4.11
- pixi environment management for reproducible builds
- GitHub Actions deployment workflow to cranmer.github.io
- Publications page (`/publications.html`) generated from BibTeX
- Presentations page (`/presentations.html`) with 113 talks from IRIS-HEP format YAML
- Video camera icons for presentations with recordings
- `pelican-presentations` plugin (separate repository) for IRIS-HEP compatible presentations
- Bluesky social link with custom butterfly icon
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

## [Pre-Migration] - Original TheoryAndPractice

The original site was maintained at https://github.com/cranmer/TheoryAndPractice using:
- Pelican 3.7.1
- Various pelican-plugins as git submodules
- Manual deployment process

See the original repository for historical changes.
