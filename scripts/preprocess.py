"""
Runs a file through the Mako template engine. Intended for use with
asset files that need to be preprocessed with Python variables/logic
before compilation.
"""

import json
import os
from path import path
import sys

from mako.template import Template

if len(sys.argv) != 2:
    sys.stderr.write("Usage: preprocess.py <filename>\n")
    sys.exit(1)

# specified as an environment variable.  Typically this is set
# in the service's upstart script and corresponds exactly to the service name.
# Service variants apply config differences via env and auth JSON files,
# the names of which correspond to the variant.
SERVICE_VARIANT = os.environ.get('SERVICE_VARIANT', None)

# when not variant is specified we attempt to load an unvaried
# config set.
CONFIG_PREFIX = ""

if SERVICE_VARIANT:
    CONFIG_PREFIX = SERVICE_VARIANT + "."

# Configure path information
REPO_ROOT = path(__file__).abspath().dirname().dirname()
ENV_ROOT = REPO_ROOT.dirname()

# Don't blow up if the environment config file doesn't exist, as it
# won't in most dev environments.
try:
    with open(ENV_ROOT / CONFIG_PREFIX + "env.json") as env_file:
        ENV_TOKENS = json.load(env_file)
except IOError:
    ENV_TOKENS = {}

# Run the file through the template engine
print Template(filename=sys.argv[1]).render(env=ENV_TOKENS)
