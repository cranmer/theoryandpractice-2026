"""
Pelican Media Plugin
====================

Generates a media & outreach page from YAML data.

Configuration:
    MEDIA_SRC: Path to YAML file with media items

YAML format:
    settings:
      default_view: cards  # or list

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

    items:
      - title: "Article Title"
        outlet: "New York Times"
        category: articles
        date: 2015-12-16
        url: "https://..."
        description: "Optional description"
        featured: true
        image: "/images/media/item.jpg"
        embed:
          type: youtube  # youtube, vimeo, audio, image
          id: "video_id"  # for youtube/vimeo
          src: "url"  # for audio/image
"""

import logging
import os
from datetime import datetime, date

from pelican import signals

logger = logging.getLogger(__name__)

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logger.warning('pelican-media: PyYAML not available')


def parse_date(date_val):
    """Parse date from various formats, always returns datetime."""
    if date_val is None:
        return None
    if isinstance(date_val, datetime):
        return date_val
    # YAML parses dates as datetime.date objects
    if isinstance(date_val, date):
        return datetime.combine(date_val, datetime.min.time())
    if isinstance(date_val, str):
        try:
            return datetime.strptime(date_val, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_val, '%Y-%m')
            except ValueError:
                try:
                    return datetime.strptime(date_val, '%Y')
                except ValueError:
                    return None
    # Try to convert if it's something else
    if hasattr(date_val, 'year'):
        try:
            return datetime(date_val.year, getattr(date_val, 'month', 1), getattr(date_val, 'day', 1))
        except (TypeError, ValueError):
            return None
    return None


def add_media(generator):
    """Add media data to the generator context."""
    if not YAML_AVAILABLE:
        return

    yaml_path = generator.settings.get('MEDIA_SRC')
    if not yaml_path:
        return

    # Resolve path relative to project root
    if not os.path.isabs(yaml_path):
        content_path = generator.settings.get('PATH', 'content')
        base_path = os.path.dirname(content_path) if content_path != 'content' else '.'
        yaml_path = os.path.join(base_path, yaml_path)

    if not os.path.exists(yaml_path):
        logger.warning(f'pelican-media: YAML file not found: {yaml_path}')
        return

    # Load YAML
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        logger.error(f'pelican-media: failed to parse {yaml_path}: {e}')
        return

    # Extract settings
    settings = data.get('settings', {})
    default_view = settings.get('default_view', 'cards')

    # Extract categories
    categories_data = data.get('categories', [])
    categories = {cat['id']: cat for cat in categories_data}

    # Process items
    items = data.get('items', [])

    for item in items:
        # Parse date
        if 'date' in item:
            item['date_obj'] = parse_date(item['date'])
            if item['date_obj']:
                item['year'] = item['date_obj'].year
            else:
                item['year'] = None
        else:
            item['date_obj'] = None
            item['year'] = None

        # Set defaults
        if 'featured' not in item:
            item['featured'] = False
        if 'description' not in item:
            item['description'] = ''

        # Get category info
        cat_id = item.get('category', '')
        if cat_id in categories:
            item['category_title'] = categories[cat_id].get('title', cat_id)
            item['category_icon'] = categories[cat_id].get('icon', 'fa-file')
        else:
            item['category_title'] = cat_id
            item['category_icon'] = 'fa-file'

    # Sort by featured (first), then by date (newest first)
    items.sort(key=lambda x: (
        not x.get('featured', False),
        -(x.get('date_obj') or datetime.min).timestamp() if x.get('date_obj') else 0
    ))

    # Get unique years for filtering
    years = sorted(set(item['year'] for item in items if item['year']), reverse=True)

    # Group by category
    def group_by_category(item_list):
        result = []
        for cat_data in categories_data:
            cat_id = cat_data['id']
            cat_items = [i for i in item_list if i.get('category') == cat_id]
            if cat_items:
                result.append({
                    'id': cat_id,
                    'title': cat_data.get('title', cat_id),
                    'icon': cat_data.get('icon', 'fa-file'),
                    'description': cat_data.get('description', ''),
                    'media_items': cat_items,
                })
        return result

    # Add to context
    generator.context['media'] = {
        'settings': {
            'default_view': default_view,
        },
        'categories': group_by_category(items),
        'all_categories': categories_data,
        'all_items': items,
        'years': years,
        'total_count': len(items),
    }

    logger.info(f'pelican-media: loaded {len(items)} media items')


def register():
    """Register the plugin with Pelican."""
    signals.generator_init.connect(add_media)
