"""
Edraak internationalization tasks.
"""
from paver.easy import task, sh
from git import Repo

from .utils.cmd import django_cmd

git_repo = Repo('.')


@task
def clean_repo_check():
    """
    Start with clean translation state.
    """
    clean_git_repo_msg = (
        'The repo has local modifications. '
        'Please stash or commit your changes.'
    )

    assert not git_repo.is_dirty(untracked_files=True), clean_git_repo_msg


@task
def i18n_theme_generate():
    """
    Run the theme's generate script.
    """
    sh(django_cmd('lms', 'devstack', 'i18n_theme_generate'))
