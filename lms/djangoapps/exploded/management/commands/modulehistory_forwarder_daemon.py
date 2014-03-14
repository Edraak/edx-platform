from django.core.management.base import BaseCommand, CommandError
from exploded.daemon import run_daemon

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **kwargs):
        import exploded.daemon; run_daemon()
