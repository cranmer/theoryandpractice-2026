"""
Pelican Projects Plugin
=======================

Generates a projects page with cards organized by category.

Configuration:
    PROJECTS_SRC: Path to YAML file with project definitions

YAML format:
    settings:
      default_card_style: image  # or minimal

    categories:
      - id: software
        title: "Software"
        description: "Open source projects"

    projects:
      - name: "Project Name"
        slug: "project-slug"
        category: software
        status: active  # active, completed, archived
        featured: true
        description: "Brief description"
        image: "/images/projects/project.png"
        url: "https://..."
        github: "owner/repo"
        tags: ["tag1", "tag2"]
        start_year: 2020
        end_year: null
        collaborators: ["Person Name"]
"""

import logging
import os

from pelican import signals

logger = logging.getLogger(__name__)

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logger.warning('pelican-projects: PyYAML not available')


def get_github_social_image(repo):
    """Generate GitHub social preview image URL.

    Args:
        repo: GitHub repo in 'owner/repo' format

    Returns:
        URL string for the repo's social image
    """
    if not repo:
        return None
    return f'https://opengraph.githubassets.com/1/{repo}'


def add_projects(generator):
    """Add projects data to the generator context."""
    if not YAML_AVAILABLE:
        return

    yaml_path = generator.settings.get('PROJECTS_SRC')
    if not yaml_path:
        return

    # Resolve path relative to project root (not content directory)
    if not os.path.isabs(yaml_path):
        content_path = generator.settings.get('PATH', 'content')
        base_path = os.path.dirname(content_path) if content_path != 'content' else '.'
        yaml_path = os.path.join(base_path, yaml_path)

    if not os.path.exists(yaml_path):
        logger.warning(f'pelican-projects: YAML file not found: {yaml_path}')
        return

    # Load YAML
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        logger.error(f'pelican-projects: failed to parse {yaml_path}: {e}')
        return

    # Extract settings
    settings = data.get('settings', {})
    default_card_style = settings.get('default_card_style', 'image')

    # Extract categories
    categories_data = data.get('categories', [])
    categories = {cat['id']: cat for cat in categories_data}

    # Process projects
    projects = data.get('projects', [])
    for project in projects:
        # Apply default card style if not specified
        if 'card_style' not in project:
            project['card_style'] = default_card_style

        # Ensure lists exist
        if 'tags' not in project:
            project['tags'] = []
        if 'collaborators' not in project:
            project['collaborators'] = []

        # Generate slug if not provided
        if 'slug' not in project:
            project['slug'] = project.get('name', '').lower().replace(' ', '-')

        # Set default status
        if 'status' not in project:
            project['status'] = 'active'

        # Set default featured
        if 'featured' not in project:
            project['featured'] = False

        # Auto-generate image from GitHub if not specified
        if not project.get('image') and project.get('github'):
            project['image'] = get_github_social_image(project['github'])

    # Group projects by category
    projects_by_category = []
    for cat_data in categories_data:
        cat_id = cat_data['id']
        cat_projects = [p for p in projects if p.get('category') == cat_id]

        # Sort by featured (first), then by start_year (most recent first), then by name
        cat_projects.sort(key=lambda p: (
            not p.get('featured', False),  # Featured first (False < True, so negate)
            -(p.get('start_year') or 0),   # Most recent first
            p.get('name', '')              # Alphabetical
        ))

        projects_by_category.append({
            'id': cat_id,
            'title': cat_data.get('title', cat_id),
            'description': cat_data.get('description', ''),
            'projects': cat_projects,
        })

    # Add to context
    generator.context['projects'] = {
        'settings': {
            'default_card_style': default_card_style,
        },
        'categories': projects_by_category,
        'all_projects': projects,
    }

    logger.info(f'pelican-projects: loaded {len(projects)} projects in {len(categories)} categories')


def register():
    """Register the plugin with Pelican."""
    signals.generator_init.connect(add_projects)
