from django.core.management.base import BaseCommand, CommandError
from exploded.daemon import StudentModuleHistoryDeDuper

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **kwargs):
        deduper = StudentModuleHistoryDeDuper()
        deduper.run_daemon()
