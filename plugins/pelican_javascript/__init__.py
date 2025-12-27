"""
Include JavaScript and CSS files for Pelican
============================================

This plugin allows you to easily embed JS and CSS in the header of individual
articles and pages using metadata:
    Stylesheets: file1.css, file2.css
    JavaScripts: file1.js, file2.js

Files are copied from content/css and content/js to output/css and output/js.
External URLs (http:// or https://) are used directly.
"""
import os
import shutil
from pelican import signals


def copy_resources(src, dest, file_list):
    """Copy files from content folder to output folder."""
    if not os.path.exists(dest):
        os.makedirs(dest)
    for file_ in file_list:
        file_src = os.path.join(src, file_)
        if os.path.exists(file_src):
            shutil.copy2(file_src, dest)


def add_files(gen, metadata):
    """
    The registered handler for the dynamic resources plugin.
    Adds javascripts and/or stylesheets to the article/page metadata.
    """
    site_url = gen.settings.get('SITEURL', '')
    relative_urls = gen.settings.get('RELATIVE_URLS', False)

    formatters = {
        'stylesheets': '<link rel="stylesheet" href="{0}" type="text/css" />',
        'javascripts': '<script src="{0}"></script>'
    }
    dirnames = {
        'stylesheets': 'css',
        'javascripts': 'js'
    }

    for key in ['stylesheets', 'javascripts']:
        if key in metadata:
            files = [f.strip() for f in metadata[key].replace(" ", "").split(",")]
            htmls = []
            for f in files:
                if f.startswith('http://') or f.startswith('https://'):
                    link = f
                else:
                    if relative_urls:
                        link = "%s/%s" % (dirnames[key], f)
                    else:
                        link = "%s/%s/%s" % (site_url, dirnames[key], f)
                html = formatters[key].format(link)
                htmls.append(html)
            metadata[key] = htmls


def move_resources(gen):
    """Move files from js/css folders to output folder."""
    js_files = gen.get_files('js', extensions=['js'])
    css_files = gen.get_files('css', extensions=['css'])

    js_dest = os.path.join(gen.output_path, 'js')
    copy_resources(gen.path, js_dest, js_files)

    css_dest = os.path.join(gen.output_path, 'css')
    copy_resources(gen.path, css_dest, css_files)


def register():
    """Plugin registration."""
    signals.article_generator_context.connect(add_files)
    signals.page_generator_context.connect(add_files)
    signals.article_generator_finalized.connect(move_resources)
