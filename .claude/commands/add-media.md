# Add Media Entry

Add a new media/outreach entry to the website.

## Input
The user will provide details in natural language, possibly including a URL. Extract whatever information is available. If a URL is provided, fetch it to get missing details like title, date, and outlet.

## Categories
The media page has these categories (use the `id` value):
- `podcasts` — Podcasts & Radio (icon: fa-podcast)
- `articles` — News Articles (icon: fa-newspaper-o)
- `interviews` — Interviews (icon: fa-microphone)
- `mentions` — Quoted In (icon: fa-quote-left) — for articles where Kyle is just quoted
- `outreach` — Outreach (icon: fa-users) — public lectures, science festivals, etc.

## Required fields
- `title`
- `outlet` (publication/organization name)
- `category` (one of the IDs above)
- `date` (YYYY-MM-DD)

## Optional fields
- `description` (brief summary)
- `url` (link to the article/media)
- `featured` (true/false)
- `image` (path to local image, e.g., `/images/foo.png`)
- `embed` (for YouTube/Vimeo video embeds):
  ```yaml
  embed:
    type: youtube  # or vimeo
    id: "VIDEO_ID"
  ```

## File to edit
`content/media.yml`

## Format
Entries go under `items:`, grouped by category section. Insert in chronological order (newest first) within the appropriate category section. Follow this YAML format:

```yaml
  - title: "Article or Media Title"
    outlet: "Publication Name"
    category: articles
    date: YYYY-MM-DD
    description: "Brief description"
    url: "https://example.com/article"
```

## Category sections in the file
The file is organized with comment headers:
```
# Podcasts & Radio
# News Articles
# Interviews
# Quoted In (Mentions)
# Outreach
```

## Instructions
1. Read `content/media.yml` to find the appropriate category section
2. If a URL is provided, fetch it to extract title, date, outlet, and description
3. Determine the correct category based on the content type and user input
4. Insert the entry in chronological order within its category section
5. For outreach items with YouTube videos, add an `embed` block for card previews
6. After editing, rebuild the site with `pixi run pelican content -s pelicanconf.py`

## User input
$ARGUMENTS
