# pelican-media

A Pelican plugin for displaying media appearances and outreach organized by category with card-based layout.

## Features

- **YAML-based configuration**: Define media items in a simple YAML file
- **Category grouping**: Organize by videos, podcasts, articles, interviews
- **Card and list views**: Toggle between card grid and compact list view
- **Category filtering**: Filter by media type
- **Year filtering**: Filter by year
- **Embedded content**: Support for YouTube, Vimeo, audio players, and images
- **Featured items**: Highlight key appearances
- **Flexible sorting**: Featured first, then by date (newest first)

## Installation

1. Copy the `pelican-media` directory to your `plugins/` folder
2. Add to your `pelicanconf.py`:

```python
PLUGIN_PATHS = ['plugins']
PLUGINS = [
    # ... other plugins
    'pelican-media',
]

# Path to media YAML file
MEDIA_SRC = 'content/media.yml'

# Add 'media' to direct templates
DIRECT_TEMPLATES = ['index', 'categories', 'authors', 'archives', 'media']
```

## YAML Schema

```yaml
settings:
  default_view: cards  # or 'list'

categories:
  - id: videos
    title: "Videos"
    icon: "fa-video-camera"
  - id: podcasts
    title: "Podcasts"
    icon: "fa-podcast"
  - id: articles
    title: "News Articles"
    icon: "fa-newspaper-o"
  - id: interviews
    title: "Interviews"
    icon: "fa-microphone"

items:
  - title: "Article or Video Title"
    outlet: "New York Times"
    category: articles
    date: 2015-12-16
    url: "https://..."
    description: "Optional description"
    featured: true
    image: "/images/media/thumbnail.jpg"
    embed:
      type: youtube  # youtube, vimeo, audio, image
      id: "dQw4w9WgXcQ"  # for youtube/vimeo
```

### Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Title of the media item |
| `outlet` | string | Yes | Media outlet name (NYT, WIRED, etc.) |
| `category` | string | Yes | Category ID |
| `date` | date | No | Publication date (YYYY-MM-DD) |
| `url` | string | No | Link to the article/video |
| `description` | string | No | Brief description |
| `featured` | boolean | No | Show first (default: false) |
| `image` | string | No | Thumbnail image URL |
| `embed` | object | No | Embedded content configuration |

### Embed Types

**YouTube:**
```yaml
embed:
  type: youtube
  id: "video_id"
```

**Vimeo:**
```yaml
embed:
  type: vimeo
  id: "video_id"
```

**Audio:**
```yaml
embed:
  type: audio
  src: "https://example.com/audio.mp3"
```

**Image:**
```yaml
embed:
  type: image
  src: "/images/media/photo.jpg"
```

## Template

Create `templates/media.html` in your theme. The plugin provides:

```jinja2
{{ media.settings }}        {# Settings dict #}
{{ media.categories }}      {# List of categories, each with .media_items #}
{{ media.all_categories }}  {# List of category definitions #}
{{ media.all_items }}       {# Flat list of all items #}
{{ media.years }}           {# List of years for filtering #}
{{ media.total_count }}     {# Total number of items #}

{# Each category has: #}
{% for cat in media.categories %}
  {{ cat.id }}              {# Category id #}
  {{ cat.title }}           {# Category title #}
  {{ cat.icon }}            {# FontAwesome icon class #}
  {{ cat.media_items }}     {# List of items in this category #}
{% endfor %}
```

## Helper Script

Use `scripts/search_media.py` to search for new media mentions:

```bash
pixi run search-media
```

## License

MIT License
