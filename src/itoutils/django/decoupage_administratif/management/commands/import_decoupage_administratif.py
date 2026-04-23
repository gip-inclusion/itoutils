from __future__ import annotations

from collections.abc import Callable

from django.core.management import BaseCommand

from itoutils.django.commands import AtomicHandleMixin, LoggedCommandMixin, dry_runnable
from itoutils.django.decoupage_administratif.importer import DecoupageAdministratifImporter


class Command(LoggedCommandMixin, AtomicHandleMixin, BaseCommand):
    help = "Import the cities, departments, EPCI and regions from the Découpage Administratif API."
    ATOMIC_HANDLE = True

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--scope",
            choices=["all", "regions", "departements", "epci", "communes"],
            default="all",
            help="Restrict the import to a specific entity type (default: all).",
        )
        parser.add_argument("--wet-run", dest="wet_run", action="store_true")

    @dry_runnable
    def handle(self, *args, **options) -> None:
        scope: str = options["scope"]
        importer = DecoupageAdministratifImporter()
        actions: dict[str, Callable[[], None]] = {
            "all": importer.import_all,
            "regions": importer.import_regions,
            "departements": importer.import_departements,
            "epci": importer.import_epci,
            "communes": importer.import_communes,
        }

        self.stdout.write(self.style.NOTICE(f"Starting import '{scope}'..."))
        actions[scope]()
        self.stdout.write(self.style.SUCCESS("Import completed."))
