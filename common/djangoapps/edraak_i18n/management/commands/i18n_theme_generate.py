# * Handling merge/forks of UserProfile.meta
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from subprocess import call
import polib
from shutil import copyfileobj


class Command(BaseCommand):
    help = '''Generate Edraak theme translation strings.'''

    @staticmethod
    def remove_ignored_messages(theme_root):
        """
        Removes all ignored translations that is has the following comment:

        # Translators: Edraak-ignore
        """
        theme_pofile = theme_root / 'conf/locale/en/LC_MESSAGES/edraak-platform-2015-theme.po'
        theme_po = polib.pofile(theme_pofile)

        # `reversed()` is used to allow removing from the bottom
        # instead of changing the index and introducing bugs
        for entry in reversed(theme_po):
            if 'edraak-ignore' in entry.comment.lower():
                theme_po.remove(entry)
                print 'Removed ignored translation: ', entry.msgid, '=>', entry.msgstr

        theme_po.save()

    @staticmethod
    def generate_pofile(theme_root):
        """
        Run pybabel to collect the translatable strings from all Mako templates in the theme.
        """
        mako_pofile_relative = 'conf/locale/en/LC_MESSAGES/mako.po'
        mako_pofile = theme_root / mako_pofile_relative

        if not mako_pofile.dirname().exists():
            os.makedirs(mako_pofile.dirname())

        open(mako_pofile, 'w').close()  # Make sure the file exists and empty

        call([
            'pybabel',
            '-q', 'extract',
            '--mapping=conf/locale/babel_mako.cfg',
            '--add-comments', 'Translators:',
            '--keyword', 'interpolate',
            '.',
            '--output={}'.format(mako_pofile_relative),
        ], cwd=theme_root)

        call(['i18n_tool', 'segment', '--config', 'conf/locale/config.yaml', 'en'], cwd=theme_root)

        if mako_pofile.exists():
            mako_pofile.unlink()

    @staticmethod
    def copy_pofile(theme_root):
        """
        Copies the pofile to the platform so the i18n_robot_pull/push can use.
        """
        theme_pofile_relative = 'conf/locale/en/LC_MESSAGES/edraak-platform-2015-theme.po'

        source = os.path.join(theme_root, theme_pofile_relative)
        dest = os.path.join(settings.REPO_ROOT, theme_pofile_relative)

        # Simulates a Linux $ cat theme/django.po > platform/django.po
        with open(source) as source_file:
            with open(dest, 'w') as dest_file:
                copyfileobj(source_file, dest_file)

    def handle(self, *args, **options):
        """
        The main command function.
        """
        if settings.FEATURES.get('USE_CUSTOM_THEME', False) and settings.THEME_NAME:
            theme_root = settings.ENV_ROOT / "themes" / settings.THEME_NAME
            self.generate_pofile(theme_root)
            self.remove_ignored_messages(theme_root)
            self.copy_pofile(theme_root)
        else:
            print "Error: theme files not found."
            print "Are you sure the config is correct? Press <Enter> to continue without theme i18n..."
            raw_input()
