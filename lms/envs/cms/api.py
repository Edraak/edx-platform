"""
Settings for the LMS that runs alongside the CMS on AWS
"""

from .dev import *

INSTALLED_APPS += (
    'tastypie',
)
