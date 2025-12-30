"""
Pelican Collaborators Plugin
============================

Generates a collaborators/team page with photos organized by category.

Configuration:
    COLLABORATORS_SRC: Path to YAML file with collaborator definitions

YAML format:
    settings:
      default_image_shape: circular  # or rectangular
      image_size: 150px

    categories:
      - id: current-students
        title: "Current Students"
      - id: former-students
        title: "Former Students"

    people:
      - name: "Jane Doe"
        category: current-students
        role: "PhD Student"
        affiliation: "University of Wisconsin-Madison"
        start_year: 2022
        end_year: null
        photo: "/images/collaborators/jane-doe.jpg"
        image_shape: circular
        graduation_year: null
        thesis_title: null
        thesis_url: null
        current_position: null
        links:
          website: "https://..."
          github: "username"
          scholar: "id"
        publications:
          - BibtexKey1
        projects:
          - project-slug
        bio: "Brief bio..."
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
    logger.warning('pelican-collaborators: PyYAML not available')


def add_collaborators(generator):
    """Add collaborators data to the generator context."""
    if not YAML_AVAILABLE:
        return

    yaml_path = generator.settings.get('COLLABORATORS_SRC')
    if not yaml_path:
        return

    # Resolve path relative to project root (not content directory)
    if not os.path.isabs(yaml_path):
        # Get the base path (parent of content directory)
        content_path = generator.settings.get('PATH', 'content')
        base_path = os.path.dirname(content_path) if content_path != 'content' else '.'
        yaml_path = os.path.join(base_path, yaml_path)

    if not os.path.exists(yaml_path):
        logger.warning(f'pelican-collaborators: YAML file not found: {yaml_path}')
        return

    # Load YAML
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        logger.error(f'pelican-collaborators: failed to parse {yaml_path}: {e}')
        return

    # Extract settings
    settings = data.get('settings', {})
    default_image_shape = settings.get('default_image_shape', 'circular')
    default_image_size = settings.get('image_size', '150px')

    # Extract categories
    categories_data = data.get('categories', [])
    categories = {cat['id']: cat for cat in categories_data}

    # Process people
    people = data.get('people', [])
    for person in people:
        # Apply default image shape if not specified
        if 'image_shape' not in person:
            person['image_shape'] = default_image_shape

        # Ensure lists exist
        if 'publications' not in person:
            person['publications'] = []
        if 'projects' not in person:
            person['projects'] = []
        if 'links' not in person:
            person['links'] = {}

    # Group people by category
    people_by_category = []
    for cat_data in categories_data:
        cat_id = cat_data['id']
        cat_people = [p for p in people if p.get('category') == cat_id]

        # Sort by start_year (most recent first), then by name
        cat_people.sort(key=lambda p: (-(p.get('start_year') or 0), p.get('name', '')))

        people_by_category.append({
            'id': cat_id,
            'title': cat_data.get('title', cat_id),
            'description': cat_data.get('description', ''),
            'people': cat_people,
        })

    # Add to context
    generator.context['collaborators'] = {
        'settings': {
            'default_image_shape': default_image_shape,
            'image_size': default_image_size,
        },
        'categories': people_by_category,
        'all_people': people,
    }

    logger.info(f'pelican-collaborators: loaded {len(people)} collaborators in {len(categories)} categories')


def register():
    """Register the plugin with Pelican."""
    signals.generator_init.connect(add_collaborators)
