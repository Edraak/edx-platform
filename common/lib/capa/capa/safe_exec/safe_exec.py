"""Capa's specialized use of codejail.safe_exec."""

from codejail.safe_exec import safe_exec as codejail_safe_exec
from codejail.safe_exec import not_safe_exec as codejail_not_safe_exec
from codejail.safe_exec import json_safe, SafeExecException
from . import lazymod
from dogapi import dog_stats_api

import hashlib
import re

# Establish the Python environment for Capa.
# Capa assumes float-friendly division always.
# The name "random" is a properly-seeded stand-in for the random module.
CODE_PROLOG = """\
from __future__ import division

import random as random_module
import sys
random = random_module.Random(%r)
random.Random = random_module.Random
sys.modules['random'] = random
"""

ASSUMED_IMPORTS=[
    ("numpy", "numpy"),
    ("math", "math"),
    ("scipy", "scipy"),
    ("calc", "calc"),
    ("eia", "eia"),
    ("chemcalc", "chem.chemcalc"),
    ("chemtools", "chem.chemtools"),
    ("miller", "chem.miller"),
    ("draganddrop", "verifiers.draganddrop"),
]

# We'll need the code from lazymod.py for use in safe_exec, so read it now.
lazymod_py_file = lazymod.__file__
if lazymod_py_file.endswith("c"):
    lazymod_py_file = lazymod_py_file[:-1]

lazymod_py = open(lazymod_py_file).read()

LAZY_IMPORTS = [lazymod_py]
for name, modname in ASSUMED_IMPORTS:
    LAZY_IMPORTS.append("{} = LazyModule('{}')\n".format(name, modname))

LAZY_IMPORTS = "".join(LAZY_IMPORTS)

def normalize_indentation(python_code):
    '''
    Check the first line of the supplied python code to determine if it is indented at all.
    As this python code should always begin with no indentation (to adhere to python indentation
    rules), remove from all lines the number of indentation spaces found so that all lines
    will be properly indented--provided all the *relative* indentation is done properly.

       (pretend this column | is column zero for this illustration)
                            |
                            V

    For example, if the user wanted to construct a python function which worked like this:
                            def hello():
                                msg = 'hello, world!'
                                if msg:
                                    print msg

    she might supply this fragment of code:
                                msg = 'hello, world!'
                                if msg:
                                    print msg

    but should have supplied the fragment without indentation like this:
                            msg = 'hello, world!'
                            if msg:
                                print msg

    @param python_code: a string of python code to which normalization should be applied
    @return: the python_code with the appropriate number of leading spaces removed (if any)
    '''
    try:
        pattern = re.compile(r'(\s*)\n([^\S]*)')   # search for unwanted indentation on the first line of code
                                                    # group 0: any all whitespace lines -- which we will ignore
                                                    # group 1: any whitespace between \n and code
        match = pattern.match(python_code)
        if match:
            replacement_pattern = '\n' + match.groups()[1]
            normalized_python_code = python_code.replace(replacement_pattern, '\n')
            python_code = normalized_python_code
    except:         # pylint: disable=bare-except
        pass        # if an exception is thrown for some reason, we consume it and just pass back the original string


    return python_code

def update_hash(hasher, obj):
    """
    Update a `hashlib` hasher with a nested object.

    To properly cache nested structures, we need to compute a hash from the
    entire structure, canonicalizing at every level.

    `hasher`'s `.update()` method is called a number of times, touching all of
    `obj` in the process.  Only primitive JSON-safe types are supported.

    """
    hasher.update(str(type(obj)))
    if isinstance(obj, (tuple, list)):
        for e in obj:
            update_hash(hasher, e)
    elif isinstance(obj, dict):
        for k in sorted(obj):
            update_hash(hasher, k)
            update_hash(hasher, obj[k])
    else:
        hasher.update(repr(obj))


@dog_stats_api.timed('capa.safe_exec.time')
def safe_exec(code, globals_dict, random_seed=None, python_path=None, cache=None, slug=None, unsafely=False):
    """
    Execute python code safely.

    `code` is the Python code to execute.  It has access to the globals in `globals_dict`,
    and any changes it makes to those globals are visible in `globals_dict` when this
    function returns.

    `random_seed` will be used to see the `random` module available to the code.

    `python_path` is a list of directories to add to the Python path before execution.

    `cache` is an object with .get(key) and .set(key, value) methods.  It will be used
    to cache the execution, taking into account the code, the values of the globals,
    and the random seed.

    `slug` is an arbitrary string, a description that's meaningful to the
    caller, that will be used in log messages.

    If `unsafely` is true, then the code will actually be executed without sandboxing.

    """
    # Check the cache for a previous result.
    if cache:
        safe_globals = json_safe(globals_dict)
        md5er = hashlib.md5()
        md5er.update(repr(code))
        update_hash(md5er, safe_globals)
        key = "safe_exec.%r.%s" % (random_seed, md5er.hexdigest())
        cached = cache.get(key)
        if cached is not None:
            # We have a cached result.  The result is a pair: the exception
            # message, if any, else None; and the resulting globals dictionary.
            emsg, cleaned_results = cached
            globals_dict.update(cleaned_results)
            if emsg:
                raise SafeExecException(emsg)
            return

    # Create the complete code we'll run.
    code_prolog = CODE_PROLOG % random_seed

    # Decide which code executor to use.
    if unsafely:
        exec_fn = codejail_not_safe_exec
    else:
        exec_fn = codejail_safe_exec

    # Run the code!  Results are side effects in globals_dict.
    try:
        code = normalize_indentation(code)      # remove any excess indentation
        exec_fn(
            code_prolog + LAZY_IMPORTS + code, globals_dict,
            python_path=python_path, slug=slug,
        )
    except SafeExecException as e:
        emsg = e.message
    else:
        emsg = None

    # Put the result back in the cache.  This is complicated by the fact that
    # the globals dict might not be entirely serializable.
    if cache:
        cleaned_results = json_safe(globals_dict)
        cache.set(key, (emsg, cleaned_results))

    # If an exception happened, raise it now.
    if emsg:
        raise e

