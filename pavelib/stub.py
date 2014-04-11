"""
Run and manage stubs for local development.
"""
from __future__ import print_function
import sys
from paver.easy import *
from .utils.cmd import cmd
from .utils.process import run_process

from path import path

DEFAULT_PORT = {"lti": 8765, "youtube": 8031}

def run_stub(stub, port=None):
    """
    Start the specified stub.

    `settings` is the Django settings module to use; if not provided, use the default.
    `port` is the port to run the server on; if not provided, use the default port for the system.
    """
    sys.path.append('/edx/app/edxapp/edx-platform/common/djangoapps/terrain')

    if stub not in ['lti', 'youtube']:
        print("Stub must be either lti or youtube", file=sys.stderr)
        exit(1)

    if port is None:
        port = DEFAULT_PORT[stub]
    import ipdb; ipdb.set_trace()
    run_process(cmd('python', '-m', 'stubs.start', stub, port))

@task
@needs('pavelib.prereqs.install_prereqs')
@cmdopts([
    ("port=", "p", "Port"),
])
def lti(options):
    """
    Run the LTI stub.
    """
    port = getattr(options, 'port', None)
    run_stub('lti', port=port)

