##
## One-off script to export 6.002x users into the edX framework
##
## Could be modified to be general by:
## * Changing user_keys and up_keys to handle dates more cleanly
## * Providing a generic set of tables, rather than just users and user profiles
## * Handling certificates and grades
## * Handling merge/forks of UserProfile.meta


from django.core.management.base import BaseCommand
from django.conf import settings
from subprocess import call
import logging


class Command(BaseCommand):
    help = '''Run theme's ./scripts/edraak_i18n_theme_push.sh'''

    def handle(self, *args, **options):
        if settings.THEME_NAME:
            theme_root = settings.ENV_ROOT / "themes" / settings.THEME_NAME
            script_path = theme_root / 'scripts/edraak_i18n_theme_push.sh'

            if script_path.exists():
                call(script_path)
                return

        print "Skipping theme push. Are you sure the config is correct? Press <Enter> to continue without theme..."
        raw_input()
