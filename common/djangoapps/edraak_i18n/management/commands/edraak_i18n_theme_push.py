# * Handling merge/forks of UserProfile.meta
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import polib
from subprocess import call


class Command(BaseCommand):
    help = '''Collects theme's translation strings and push it to transifex.'''

    @staticmethod
    def remove_ignored_messages(theme_root):
        """
        Removes the already translated strings from the custom translation string based on `django.po`.

        i.e. if it is in django.po, remove it from the custom pofile.

            edraak-platform-theme.po = strings-in-edraak-theme - translated_in_django.po

        :param theme_root: The root path of the theme.
        """
        pofile_path = theme_root / 'conf/locale/en/LC_MESSAGES/edraak-platform-theme.po'

        theme_po = polib.pofile(pofile_path)

        django_po = polib.pofile(settings.REPO_ROOT / 'conf/locale/ar/LC_MESSAGES/django.po')

        translated_msgids = {}
        for entry in django_po:
            if entry.msgstr:
                translated_msgids[entry.msgid] = True

        # `reversed()` is used to allow removing from the bottom
        # instead of changing the index and introducing bugs
        for entry in reversed(theme_po):
            if 'edraak-override' in entry.comment.lower():
                if translated_msgids.get(entry.msgid, False):
                    theme_po.remove(entry)

        theme_po.save()

    @staticmethod
    def generate_pofile(theme_root):
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
    def transifex_push(theme_root):
        call(['tx', 'push', '-l', 'en', '-s', '-r', 'edraak.edraak-platform-theme'], cwd=theme_root)

    def handle(self, *args, **options):
        if settings.FEATURES.get('USE_CUSTOM_THEME', False) and settings.THEME_NAME:
            theme_root = settings.ENV_ROOT / "themes" / settings.THEME_NAME

            self.generate_pofile(theme_root)
            self.remove_ignored_messages(theme_root)
            self.transifex_push(theme_root)
        else:
            print "Error: theme files not found."
            print "Are you sure the config is correct? Press <Enter> to continue without theme i18n..."
            raw_input()
