Title: Migrating with Claude
date: 2025-12-29
Slug: migrating-with-claude
Category: Blog
Tags: website, Claude, agentic AI
Authors: Kyle Cranmer
Summary: I migrated my personal website from Pelican 3.7 to Pelican 4.11 using Claude Code, Anthropic's agentic AI coding tool. Here's what changed and how it went.

I've been meaning to update my personal website infrastructure for a while. The site was running on Pelican 3.7.1, which was getting long in the tooth. This December, I finally migrated to Pelican 4.11 using [Claude Code](https://claude.com/claude-code), Anthropic's agentic AI coding tool.

## Migration Overview

This repository is a fresh migration of the original [TheoryAndPractice](https://github.com/cranmer/TheoryAndPractice) repository. The migration involved several key changes:

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

## Key Changes

### Added

- Fresh repository migrated from Pelican 3.7 to Pelican 4.11
- pixi environment management for reproducible builds
- GitHub Actions deployment workflow to cranmer.github.io
- **New** CV page (`/pages/cv.html`) with bio, experience, education, awards, and professional highlights
- **New** Selected Publications page (`/selected-publications.html`) with thematic categories
    - Replaces old Publications page (`/publications.html`) generated from by `pelican-bibtex`
    - Custom `pelican-selected-publications` plugin for YAML-driven publication organization
    - Filter by category, year, and highlighted papers
    - Publication metrics section displaying total papers, citations, and h-index
    - Profile icons linking to Google Scholar, INSPIRE, arXiv, OpenAlex, and ORCiD
    - Collapsible Altmetric badges for each publication with global toggle
    - Official arXiv logomark icon
- **New** Talks page (`/presentations.html`) displaying 113 talks with video icons, compatible with [IRIS-HEP format](https://iris-hep.org/presentations/byperson.html)
    - Custom `pelican-presentations` plugin for parsing YAML presentation data
- **New** Projects page (`/projects.html`) with card-based layout organized by category
    - Custom `pelican-projects` plugin for YAML-driven project organization
    - Card and list view toggle
    - Category and status filtering (All/Active/Completed)
    - Draft mode with separate preview page (`/projects-draft.html`) for unpublished projects
    - Auto-fetch images from GitHub repos when not specified
    - SVG images automatically get white backgrounds
- [Pagefind](https://pagefind.app/) search with instant client-side search across all pages
- Bluesky social link with custom butterfly icon
- Custom SVG icons for Google Scholar, ORCiD, INSPIRE-HEP, arXiv, and OpenAlex (Font Awesome 4.x lacks these)
- Custom navbar hover color (#EE9F43 orange)
- Open Graph and Twitter Card support for social media preview cards
- BibTeX modal popups with copy-to-clipboard functionality
- Markdown rendering inside HTML blocks (`md_in_html` extension)

### Fixed

- Markdown links not rendering inside HTML `<div>` blocks
- Floating images appearing in blog index summaries
- BibTeX popup windows blocked by modern browsers (replaced with Bootstrap modals)

### Plugin Modifications and Additions

The migration required modifications to several plugins:

 * **pelican-cite**: Added Bootstrap modal for viewing BibTeX entries with copy-to-clipboard functionality.

 * **pelican-bibtex**: Added Bootstrap modal replacing the old `window.open` popups that modern browsers block.

 * **pelican_javascript**: Migrated to Pelican 4 signal API while maintaining support for per-page custom CSS and JavaScript.

 * **pelican-presentations**: A new plugin created during this migration to generate a presentations page from YAML data. It's compatible with the IRIS-HEP presentations format, groups talks by year, and displays video icons for presentations with recordings.

 * **pelican-selected-publications**: Another new plugin that generates a curated publications page organized by research themes. Publications are defined in a YAML file that references BibTeX keys, allowing thematic grouping with category descriptions. Features include filtering by category/year/highlights, publication metrics display, profile icons, and collapsible Altmetric badges.

 * **pelican-projects**: A new plugin that generates a projects page with card-based layout. Projects are organized by category (software, research, collaborations, etc.) with card and list view options, status filtering, and draft mode support. Automatically fetches social preview images from GitHub repos and handles SVG images with white backgrounds.

## Working with Claude Code

This entire migration was done in collaboration with Claude Code. The AI agent was able to:

- Understand the existing Pelican 3.7 configuration and plugin structure
- Set up the new pixi environment and Pelican 4.11 configuration
- Migrate and modify plugins to work with the new Pelican version
- Create a new `pelican-presentations` plugin from scratch, compatible with IRIS-HEP's format
- Create a new `pelican-selected-publications` plugin for thematic publication organization with Altmetric integration
- Create a new `pelican-projects` plugin for card-based project display with draft mode support
- Build a comprehensive CV page from PDF content
- Debug issues with template rendering and markdown processing
- Create the GitHub Actions deployment workflow
- Add new features like the BibTeX modals, presentations page, Pagefind search, custom social icons, publication metrics, and social media preview cards
- Implement custom CSS icons for services not supported by Font Awesome 4.x (arXiv, OpenAlex, Google Scholar, ORCiD, INSPIRE)

It was a genuinely collaborative process—I would describe what I wanted, Claude would implement it, and we'd iterate on the details together.

## Documentation

For full details on the setup and all changes made, see:

- [README.md](https://github.com/cranmer/theoryandpractice-2026/blob/main/README.md) - Complete documentation on setup, deployment, and configuration
- [CHANGELOG.md](https://github.com/cranmer/theoryandpractice-2026/blob/main/CHANGELOG.md) - Detailed list of all changes made during migration
