"""
Edraak internationalization tasks
"""
import tempfile
import os
from path import path
import yaml
from paver.easy import task, needs, sh, BuildFailure
import polib
from git import Repo
import contextlib
from shutil import copyfile
from polib import pofile, POFile
from txclib.project import Project
import openassessment

from .utils.cmd import django_cmd

EDRAAK_RESOURCES = (
    'edraak-platform',
    'edraak-platform-2015-theme',
)


POFILE_DUMMY_METADATA = {
    'Project-Id-Version': 'Edraak 1',
    'Report-Msgid-Bugs-To': 'dev@qrf.org',
    'POT-Creation-Date': '2014-12-15 11:17+0200',
    'PO-Revision-Date': 'YEAR-MO-DA HO:MI+ZONE',
    'Last-Translator': 'Edraak Dev <dev@qrf.org>',
    'Language-Team': 'Edraak Dev <dev@qrf.org>',
    'MIME-Version': '1.0',
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Transfer-Encoding': '8bit',
    'Generated-By': 'Paver',
}

ARABIC_LOCALE_DIR = 'conf/locale/ar/LC_MESSAGES/'

OTHER_RTL_LOCALES = ('eo', 'rtl', 'he',)

git_repo = Repo('.')


@contextlib.contextmanager
def working_directory(path):
    """
    A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.
    """
    prev_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_cwd)


@contextlib.contextmanager
def get_tx_pofile(resource):
    """
    Retrieves reviewed translations from Transifex into a temporary pofile.
    :param resource:
    :return: POFile
    """
    try:
        p = Project()
        p.url_info = {
            'host': 'https://www.transifex.com',
            'project': 'edx-platform',
            'resource': resource,
        }

        content, encoding = p.do_url_request('pull_reviewed_file', language='ar')

        __, content_path = tempfile.mkstemp(suffix='.po')

        with open(content_path, 'w') as content_fd:
            content_fd.write(content.encode(encoding))

        yield pofile(content_path)
    finally:
        os.remove(content_path)


def js_nonjs(func):
    """
    Make a task run for both `django.po` and `djangojs.po` in a DRY way.
    """
    def wrapper():
        """
        Run it twice.
        """
        func(is_js=False, suffix='')
        func(is_js=True, suffix='js')

    # Keep the original name for Paver
    wrapper.__name__ = func.__name__

    return wrapper


def run_for_js_nonjs(func):
    """
    Actually run the function twice, rather than decorating the function.
    """

    func2 = js_nonjs(func)
    func2()


@task
def clean_repo_check():
    # Start with clean translation state
    clean_git_repo_msg = (
        'The repo has local modifications. '
        'Please stash or commit your changes.'
    )

    assert not git_repo.is_dirty(untracked_files=True), clean_git_repo_msg


@task
def i18n_po_pull_edraak():
    # Get Edraak translations
    for resource in EDRAAK_RESOURCES:
        cmd = ' '.join([
            'tx',
            'pull',
            '--force',
            '--mode=reviewed',
            '--language=ar',
            '--resource=edraak.{}'.format(resource),
        ])

        sh(cmd)


def i18n_remove_duplicates(pofile):
    """
    Removes duplicates from a POFile list, i.e. make it unique!

    This reduces the load on the JavaScript djangojs.mo and makes
    the pavelib/edraak.py process more solid and explicit.
    """

    existing_strings = {}

    for entry in reversed(pofile):
        if entry.msgid not in existing_strings:
            existing_strings[entry.msgid] = True
        else:
            pofile.remove(entry)


@task
@js_nonjs
def i18n_edraak_generate_files(is_js, suffix):
    """
    Append all Edraak strings to the original django.mo.
    """
    with working_directory(ARABIC_LOCALE_DIR):
        django_pofile = polib.pofile('django{}.po'.format(suffix))

        resources = [
            'edraak{}-platform'.format(suffix),
            'django{}-openassessment-updates'.format(suffix),
            'django{}-updates'.format(suffix),
        ]

        if not is_js:
            resources.append('edraak-platform-2015-theme')

        for resource in resources:
            for entry in polib.pofile('{}.po'.format(resource)):
                django_pofile.append(entry)

        # Save a backup in git for later inspection,
        # and keep django.po untouched
        i18n_remove_duplicates(django_pofile)
        django_pofile.save('django{}-edraak-customized.po'.format(suffix))
        django_pofile.save_as_mofile('django{}.mo'.format(suffix))


@task
def i18n_po_pull_edx():
    # Pulling these languages to let `i18n_generate_latest()` work well,
    # This will be undoed later
    # TODO: Consider removing dummy locales
    for lang in OTHER_RTL_LOCALES + ('ar',):
        sh('tx pull --force --mode=reviewed --language={}'.format(lang))

    i18n_generate_latest()

    def create_lastest(is_js, suffix):
        with working_directory(ARABIC_LOCALE_DIR):
            latest = path('latest-django{}.po'.format(suffix))

            if latest.exists():
                latest.remove()

            copyfile('django{}.po'.format(suffix), latest)

    run_for_js_nonjs(create_lastest)

    sh('git checkout -- conf/')  # Undo brutal `i18n_tool generate` chenges


def i18n_generate_latest():
    """
    Compile localizable strings from sources, extracting strings first.
    """

    cmd = 'i18n_tool generate'
    sh(cmd + ' --rtl --strict')


@task
@js_nonjs
def i18n_make_updates(is_js, suffix):
    with working_directory(ARABIC_LOCALE_DIR):
        django_edx = polib.pofile('django{}.po'.format(suffix))
        django_latest = polib.pofile('latest-django{}.po'.format(suffix))

        edx_entries = {}
        for entry in django_edx.translated_entries():
            edx_entries[entry.msgid] = entry

        for entry in reversed(django_latest):
            if not entry.translated():
                django_latest.remove(entry)
            else:
                edx_entry = edx_entries.get(entry.msgid)
                if edx_entry and edx_entry.msgstr == entry.msgstr:
                    # Remove the ones that didn't change
                    django_latest.remove(entry)

        print 'Added {} updated translations for django{}.po:'.format(
            len(django_latest),
            suffix,
        )

        django_latest.save('django{}-updates.po'.format(suffix))
        path('latest-django{}.po'.format(suffix)).remove()


@task
@needs(
    'pavelib.edraak.clean_repo_check',
    'pavelib.i18n.i18n_clean',
    'pavelib.edraak.i18n_po_pull_edx',
    'pavelib.edraak.i18n_po_pull_edraak',
    'pavelib.edraak.i18n_edraak_ora_pull',
    'pavelib.edraak.i18n_make_updates',
    'pavelib.edraak.i18n_edraak_generate_files',
)
def i18n_edraak_pull():
    """
    Pulls  translation files.
    """
    files_to_add = (
        'edraak-platform-2015-theme.po',
        'edraak-platform.po',

        'django-edraak-customized.po',
        'djangojs-edraak-customized.po',

        'django-openassessment-updates.po',
        'djangojs-openassessment-updates.po',

        'django-updates.po',
        'djangojs-updates.po',

        'django.mo',
        'djangojs.mo',
    )

    # Undo brutal `i18n_tool generate` chenges
    for locale in OTHER_RTL_LOCALES:
        sh('git checkout -- conf/locale/{}'.format(locale))

    with working_directory(ARABIC_LOCALE_DIR):
        # Keep it to it's original state
        sh('git checkout -- django.po djangojs.po')

        for f in files_to_add:
            sh('git add --force {}'.format(f))

        default_message = 'Update Edraak translations (autogenerated message)'
        sh('git commit -m "{}"'.format(default_message))

    sh('git checkout -- conf/')  # Cleanup dirty files
    git_push()


def git_push():
    """
    A `$ git push` that fails safely, and prints a warning.
    """
    try:
        print sh('git push', capture=True)
    except BuildFailure as e:
        print 'WARN: Git is unable to push to the remote repository.'
        print '      This error will not interrupt the build.'
        print '      You can `$ git push` manully to debug the error.'


@task
def i18n_edraak_theme_push():
    """
    Pushed the theme translation strings to Transifex.
    """
    sh(django_cmd('lms', 'devstack', 'i18n_edraak_theme_push'))


@task
@needs(
    'pavelib.edraak.i18n_edraak_theme_push',
    'pavelib.i18n.i18n_extract',
)
@js_nonjs
def i18n_edraak_push(is_js, suffix):
    """
    Extracts  strings and appends it to the provided .PO file.

    It searches for translation strings that are marked
    with "# Translators: " comment.
    """

    edx_pofile = polib.pofile('conf/locale/ar/LC_MESSAGES/django{}.po'.format(suffix))

    with open("conf/locale/config.yaml", 'r') as locale_config_file:
        locale_config = yaml.load(locale_config_file)
        partial_pofiles = locale_config['generate_merge']['django{}.po'.format(suffix)]

    with working_directory('conf/locale/en/LC_MESSAGES'):
        edraak_specific_path = path('edraak{}-platform.po'.format(suffix))

        if edraak_specific_path.exists():
            edraak_specific_path.unlink()

        edraak_specific = POFile()

        edraak_specific.metadata = POFILE_DUMMY_METADATA

        for po_path in partial_pofiles:
            print 'processing', po_path

            pofile = polib.pofile(po_path)

            for entry in pofile:
                new_entry = entry not in edx_pofile
                marked_as_specific = 'edraak-specific' in entry.comment.lower()

                if new_entry or marked_as_specific:
                    edraak_specific.append(entry)

        edraak_specific.save(edraak_specific_path)

        sh('tx push -l en -s -r edraak.edraak{}-platform'.format(suffix))


@task
@js_nonjs
def i18n_edraak_ora_pull(is_js, suffix):
    module_dir = path(openassessment.__file__).dirname()
    current_pofile = pofile(module_dir / 'locale/ar/LC_MESSAGES/django{}.po'.format(suffix))

    resource_name = 'openassessment-js' if is_js else 'openassessment'

    new_pofile = POFile()

    with get_tx_pofile(resource_name) as latest_pofile:
        for entry in current_pofile:
            if not entry.translated():
                translated_entry = latest_pofile.find(entry.msgid)

                if translated_entry and translated_entry.translated():
                    new_pofile.append(translated_entry)

    with working_directory(ARABIC_LOCALE_DIR):
        new_pofile.save('django{}-openassessment-updates.po'.format(suffix))
