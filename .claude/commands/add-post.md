# Add Blog Post

Create a new blog post on the website.

## Input
The user will provide details about the post in natural language — topic, title, tags, etc. They may also provide a URL to reference material or a draft file.

## Required fields (Pelican metadata)
- `Title` — the post title
- `date` — publication date (YYYY-MM-DD, default to today)
- `Slug` — URL slug (lowercase, hyphenated version of title)
- `Category` — typically `Blog`
- `Authors` — typically `Kyle Cranmer`

## Optional fields
- `Tags` — comma-separated tags
- `Summary` — one-line summary for listings
- `JavaScripts` — e.g., MathJax CDN if math is used

## File location
Posts are markdown files in `content/`. The filename should match the slug: `content/<slug>.md`

## Format
Use Pelican's metadata header (no YAML front matter — just `Key: Value` lines), followed by a blank line, then the post body in Markdown.

```markdown
Title: Example Post Title
date: 2026-04-01
Slug: example-post-title
Category: Blog
Tags: tag1, tag2
Authors: Kyle Cranmer
Summary: A brief summary of the post.

Post body in Markdown goes here.
```

## Instructions
1. Ask the user for the topic/title if not provided via $ARGUMENTS
2. Generate the slug from the title (lowercase, hyphens, no special characters)
3. Set the date to today unless the user specifies otherwise
4. Create the file at `content/<slug>.md` with the metadata header and any initial content
5. If the user provides body content or a URL, incorporate it into the post
6. If the post uses math notation, include the MathJax JavaScript line in metadata

## User input
$ARGUMENTS
