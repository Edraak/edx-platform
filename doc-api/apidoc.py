#!/usr/bin/python

import os, subprocess
from path import path

# Root for these documents
DOC_DIR = path(__file__).abspath().dirname()
DOC_SRC_DIR = DOC_DIR.joinpath('source').normpath()

# BASE_DIR is the mitx directory
BASE_DIR = DOC_DIR.joinpath('..').normpath()

SOURCES = ('cms/djangoapps',
           'i18n',
           'lms/djangoapps',
           'lms/lib',
           'common/djangoapps',
           'common/lib/capa',
           'common/lib/xmodule'
           )

def run(command, cwd=BASE_DIR):
    subprocess.call(command.split(' '), cwd=cwd)

def rst_files():
    """
    This is a generator.
    Returns all the rst files in the doc source directory.
    """
    for name in DOC_SRC_DIR.listdir():
        (base, ext) = name.splitext()
        if ext == '.rst':
            yield DOC_SRC_DIR.joinpath(name)

def save_module(i, source):
    name = DOC_SRC_DIR.joinpath('modules.rst')
    new_name = DOC_SRC_DIR.joinpath('modules%s.rst' % i)
    if name.exists():
        os.rename(name, new_name)

def remove_setup():
    name = DOC_SRC_DIR.joinpath('setup.rst')
    if os.path.exists(name):
        os.remove(name)

def make_clean():
    """
    Delete all rst files (except for index.rst)
    """
    for name in rst_files():
        if os.path.basename(name) != 'index.rst':
            os.remove(name)

def make_apidoc():
    for (i, source) in enumerate(SOURCES):
        out_path = BASE_DIR.relpathto(DOC_SRC_DIR)
        run('sphinx-apidoc -o %s %s' % (out_path, source))
        save_module(i, source)

def make_html():
    remove_setup()
    run('make html', cwd=DOC_DIR)

def main():
    make_clean()
    make_apidoc()
    make_html()

if __name__ == '__main__':
    main()
