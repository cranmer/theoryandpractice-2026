Title: Migrating with Claude
date: 2025-12-27
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
- Publications page (`/publications.html`) generated from BibTeX
- Bluesky social link with custom butterfly icon
- BibTeX modal popups with copy-to-clipboard functionality
- Markdown rendering inside HTML blocks (`md_in_html` extension)

### Fixed

- Markdown links not rendering inside HTML `<div>` blocks
- Floating images appearing in blog index summaries
- BibTeX popup windows blocked by modern browsers (replaced with Bootstrap modals)

### Plugin Modifications

The migration required modifications to several plugins:

**pelican-cite**: Added Bootstrap modal for viewing BibTeX entries with copy-to-clipboard functionality.

**pelican-bibtex**: Added Bootstrap modal replacing the old `window.open` popups that modern browsers block.

**pelican_javascript**: Migrated to Pelican 4 signal API while maintaining support for per-page custom CSS and JavaScript.

## Working with Claude Code

This entire migration was done in collaboration with Claude Code. The AI agent was able to:

- Understand the existing Pelican 3.7 configuration and plugin structure
- Set up the new pixi environment and Pelican 4.11 configuration
- Migrate and modify plugins to work with the new Pelican version
- Debug issues with template rendering and markdown processing
- Create the GitHub Actions deployment workflow
- Add new features like the BibTeX modals and Bluesky social icon

It was a genuinely collaborative process—I would describe what I wanted, Claude would implement it, and we'd iterate on the details together.

## Documentation

For full details on the setup and all changes made, see:

- [README.md](https://github.com/cranmer/theoryandpractice-2026/blob/main/README.md) - Complete documentation on setup, deployment, and configuration
- [CHANGELOG.md](https://github.com/cranmer/theoryandpractice-2026/blob/main/CHANGELOG.md) - Detailed list of all changes made during migration
