from django.core.management import BaseCommand

from itoutils.django.commands import LoggedCommandMixin, dry_runnable


class Command(LoggedCommandMixin, BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")

    @dry_runnable
    def handle(self, **options):
        # dry_runnable handle on a command that does NOT run in a transaction
        print("Never to be seen message")
