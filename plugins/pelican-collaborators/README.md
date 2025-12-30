# pelican-collaborators

A Pelican plugin for displaying team members, students, postdocs, and collaborators with photos, organized by category with filtering support.

## Features

- **YAML-based configuration**: Define collaborators in a simple YAML file
- **Category grouping**: Organize by students, postdocs, scientists, collaborators, etc.
- **Current/Former filtering**: Toggle between current and former members
- **Auto-fetch avatars**: Automatically fetch profile photos from GitHub and Bluesky
- **Flexible image shapes**: Support for circular or rectangular photo crops
- **Rich metadata**: Track roles, affiliations, years, thesis info, current positions
- **Social links**: GitHub, Google Scholar, Twitter, LinkedIn, Bluesky, websites

## Installation

### As a local plugin

1. Copy the `pelican-collaborators` directory to your Pelican `plugins/` folder
2. Add to your `pelicanconf.py`:

```python
PLUGIN_PATHS = ['plugins']
PLUGINS = [
    # ... other plugins
    'pelican-collaborators',
]
```

### Dependencies

- `PyYAML` - for parsing the YAML configuration
- `requests` (optional) - for fetching Bluesky avatars

```bash
pip install pyyaml requests
```

## Configuration

Add to your `pelicanconf.py`:

```python
# Path to collaborators YAML file (relative to project root)
COLLABORATORS_SRC = 'content/collaborators.yml'

# Add 'collaborators' to direct templates to generate the page
DIRECT_TEMPLATES = ['index', 'categories', 'authors', 'archives', 'collaborators']
```

## YAML Schema

Create a YAML file (e.g., `content/collaborators.yml`):

```yaml
# Global settings
settings:
  default_image_shape: circular  # or 'rectangular'
  image_size: 120px

# Define categories
categories:
  - id: students
    title: "Students"
    description: "PhD students and undergraduate researchers."

  - id: postdocs
    title: "Postdocs"
    description: "Postdoctoral researchers."

  - id: scientists
    title: "Scientists"
    description: "Research scientists and staff."

  - id: collaborators
    title: "Collaborators"
    description: "Frequent research collaborators."

# Define people
people:
  # Current PhD student
  - name: "Alice Chen"
    category: students
    current: true
    role: "PhD Student"
    affiliation: "University of Wisconsin-Madison"
    start_year: 2022
    photo: null  # Will auto-fetch from GitHub
    links:
      github: "alicechen"
      scholar: "abc123"
      website: "https://alicechen.com"

  # Former student with thesis info
  - name: "Bob Martinez"
    category: students
    current: false
    role: "PhD Student"
    affiliation: "New York University"
    start_year: 2016
    end_year: 2021
    graduation_year: 2021
    thesis_title: "Machine Learning Methods for Particle Physics"
    thesis_url: "https://example.com/thesis"
    current_position: "Research Scientist at Meta AI"
    links:
      github: "bobmartinez"

  # Collaborator with rectangular photo
  - name: "Prof. Carol Johnson"
    category: collaborators
    current: true
    role: "Professor"
    affiliation: "MIT"
    image_shape: rectangular
    links:
      website: "https://caroljohnson.mit.edu"
      bluesky: "carol.bsky.social"
```

### Person Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | **Required.** Full name |
| `category` | string | **Required.** Category ID (must match a category) |
| `current` | boolean | Whether currently active (default: true) |
| `role` | string | Role/title (e.g., "PhD Student", "Professor") |
| `affiliation` | string | Institution name |
| `start_year` | integer | Year started |
| `end_year` | integer | Year ended (for former members) |
| `graduation_year` | integer | PhD graduation year |
| `thesis_title` | string | Thesis title |
| `thesis_url` | string | URL to thesis |
| `current_position` | string | Current position (for former members) |
| `photo` | string | Photo URL or local path |
| `image_shape` | string | 'circular' or 'rectangular' (overrides default) |
| `bio` | string | Brief biography |
| `links` | object | Social/web links (see below) |
| `publications` | list | List of BibTeX keys (for future integration) |
| `projects` | list | List of project slugs (for future integration) |

### Link Fields

| Field | Description | Auto-avatar |
|-------|-------------|-------------|
| `website` | Personal website URL | No |
| `github` | GitHub username | Yes |
| `bluesky` | Bluesky handle (e.g., "user.bsky.social") | Yes |
| `scholar` | Google Scholar ID | No |
| `twitter` | Twitter/X username | No |
| `linkedin` | LinkedIn username | No |

## Photo Handling

The plugin automatically fetches profile photos when no `photo` is specified:

1. **GitHub** (priority 1): Uses `https://github.com/{username}.png`
2. **Bluesky** (priority 2): Fetches from Bluesky's public API

### Manual Photo Override

```yaml
- name: "Alice Chen"
  photo: "/images/collaborators/alice.jpg"  # Local path
  links:
    github: "alicechen"  # Ignored when photo is set
```

### Downloading Photos Locally

A helper script is included to download and cache photos locally:

```bash
# Preview what would be downloaded
python scripts/fetch-collaborator-photos.py --dry-run

# Download all photos
python scripts/fetch-collaborator-photos.py

# Force re-download existing files
python scripts/fetch-collaborator-photos.py --force
```

Photos are saved to `content/images/collaborators/{name-slug}.jpg`

## Template

Create `templates/collaborators.html` in your theme. The plugin provides:

```jinja2
{{ collaborators.settings }}     {# Global settings dict #}
{{ collaborators.categories }}   {# List of categories with people #}
{{ collaborators.all_people }}   {# Flat list of all people #}
```

### Example Template Structure

```jinja2
{% extends "base.html" %}
{% block content %}
<h1>Collaborators</h1>

{% for cat in collaborators.categories %}
{% if cat.people %}
<section id="{{ cat.id }}">
    <h2>{{ cat.title }}</h2>
    <p>{{ cat.description }}</p>

    <div class="grid">
    {% for person in cat.people %}
        <div class="card {{ 'current' if person.current else 'former' }}">
            {% if person.photo %}
            <img src="{{ person.photo }}" alt="{{ person.name }}"
                 class="{{ person.image_shape }}">
            {% endif %}

            <h3>{{ person.name }}</h3>
            <p>{{ person.role }}</p>
            <p>{{ person.affiliation }}</p>

            {% if person.start_year %}
            <p>{{ person.start_year }}{% if person.end_year %} – {{ person.end_year }}{% endif %}</p>
            {% endif %}

            {% if person.current_position %}
            <p>Now: {{ person.current_position }}</p>
            {% endif %}

            <div class="links">
                {% if person.links.website %}
                <a href="{{ person.links.website }}">Website</a>
                {% endif %}
                {% if person.links.github %}
                <a href="https://github.com/{{ person.links.github }}">GitHub</a>
                {% endif %}
            </div>
        </div>
    {% endfor %}
    </div>
</section>
{% endif %}
{% endfor %}
{% endblock %}
```

## Filtering

The included template supports JavaScript-based filtering:

- **Category filter**: Dropdown to show specific categories
- **Status filter**: Toggle buttons for All / Current / Former

People within each category are sorted by `start_year` (most recent first), then by name.

## Context Variables

The plugin adds a `collaborators` dict to the Pelican context:

```python
{
    'settings': {
        'default_image_shape': 'circular',
        'image_size': '120px',
    },
    'categories': [
        {
            'id': 'students',
            'title': 'Students',
            'description': '...',
            'people': [/* list of person dicts */],
        },
        # ...
    ],
    'all_people': [/* flat list of all people */],
}
```

## License

MIT License

## Author

Kyle Cranmer
