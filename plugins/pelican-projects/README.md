# pelican-projects

A Pelican plugin for displaying projects organized by category with card-based layout.

## Features

- **YAML-based configuration**: Define projects in a simple YAML file
- **Category grouping**: Organize by software, research, teaching, etc.
- **Draft mode**: Mark projects as drafts to hide them from production builds
- **Auto-fetch images**: Automatically fetch social preview images from GitHub repos
- **Flexible sorting**: Featured projects first, then by year

## Installation

1. Copy the `pelican-projects` directory to your `plugins/` folder
2. Add to your `pelicanconf.py`:

```python
PLUGIN_PATHS = ['plugins']
PLUGINS = [
    # ... other plugins
    'pelican-projects',
]

# Path to projects YAML file
PROJECTS_SRC = 'content/projects.yml'

# Add 'projects' to direct templates
DIRECT_TEMPLATES = ['index', 'categories', 'authors', 'archives', 'projects']
```

## Configuration

### Pelican Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `PROJECTS_SRC` | None | Path to YAML file with project definitions |

### Draft Mode

Projects can be marked as drafts by setting `draft: true`. The plugin creates two contexts:

- `projects` - Only published (non-draft) projects, used by `projects.html`
- `projects_draft` - All projects including drafts, used by `projects-draft.html`

**Setup:**
```python
# In pelicanconf.py
DIRECT_TEMPLATES = ['index', 'projects', 'projects-draft']  # Include both
```

**Usage:**
- `/projects.html` - Main projects page (in navigation), shows only published projects
- `/projects-draft.html` - Preview page (not in navigation), shows all projects including drafts

This allows you to preview draft projects at any time without changing config settings.

## YAML Schema

```yaml
settings:
  default_card_style: image  # or 'minimal'

categories:
  - id: software
    title: "Software"
    description: "Open source projects"
  - id: research
    title: "Research"
    description: "Research initiatives"

projects:
  - name: "Project Name"
    slug: "project-slug"
    category: software
    status: active           # active, completed, archived
    featured: true           # Featured projects appear first
    draft: false             # Draft projects hidden in production
    description: "Brief description of the project"
    image: "/images/projects/project.png"
    url: "https://project-website.com"
    github: "owner/repo"     # Auto-generates image if none specified
    tags: ["python", "ml"]
    start_year: 2020
    end_year: null           # null for ongoing projects
    collaborators: ["Person Name"]
```

### Project Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Project name |
| `category` | string | Yes | Category ID |
| `slug` | string | No | URL slug (auto-generated from name) |
| `status` | string | No | active, completed, or archived (default: active) |
| `featured` | boolean | No | Show first in category (default: false) |
| `draft` | boolean | No | Hide from production (default: false) |
| `description` | string | No | Brief description |
| `image` | string | No | Image URL or path |
| `url` | string | No | Project website |
| `github` | string | No | GitHub repo (owner/repo format) |
| `tags` | list | No | List of tags |
| `start_year` | integer | No | Year started |
| `end_year` | integer | No | Year ended (null for ongoing) |
| `collaborators` | list | No | List of collaborator names |

## Image Handling

If no `image` is specified but a `github` repo is provided, the plugin automatically uses GitHub's social preview image:

```
https://opengraph.githubassets.com/1/{owner}/{repo}
```

## Template

Create `templates/projects.html` in your theme. The plugin provides:

```jinja2
{{ projects.settings }}     {# Settings dict #}
{{ projects.categories }}   {# List of categories with projects #}
{{ projects.all_projects }} {# Flat list of all projects #}
```

## License

MIT License
