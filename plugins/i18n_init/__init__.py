"""
Minimal i18n initialization for pelican-bootstrap3 theme.
This replaces pelican-i18n-subsites which uses deprecated Jinja2 APIs.
"""

from pelican import signals
import gettext

def init_i18n(pelican_obj):
    """Initialize Jinja2 i18n extension with null translations."""
    # Install null translations (English only, no actual translation)
    null_translations = gettext.NullTranslations()
    pelican_obj.env.install_gettext_translations(null_translations)

def register():
    signals.generator_init.connect(init_i18n)
