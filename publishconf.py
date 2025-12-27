#!/usr/bin/env python
"""Production configuration for Theory And Practice site."""

# Import all settings from pelicanconf
import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

# Production URL
SITEURL = 'https://theoryandpractice.org'
RELATIVE_URLS = False

# Enable feeds for production
FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'

# Delete output directory before regenerating
DELETE_OUTPUT_DIRECTORY = True
