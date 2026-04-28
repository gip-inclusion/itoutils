from __future__ import annotations

from collections.abc import Callable

from django.core.management import BaseCommand

from itoutils.django.commands import AtomicHandleMixin, LoggedCommandMixin, dry_runnable
from itoutils.django.decoupage_administratif.importer import DecoupageAdministratifImporter
from itoutils.django.decoupage_administratif.models import Department

OVERSEAS_DEPARTMENTS = [
    {
        "code": "975",
        "name": "Saint-Pierre-et-Miquelon",
        "normalized_name": "SAINT PIERRE ET MIQUELON",
    },
    {
        "code": "977",
        "name": "Saint-Barthélemy",
        "normalized_name": "SAINT BARTHELEMY",
    },
    {
        "code": "978",
        "name": "Saint-Martin",
        "normalized_name": "SAINT MARTIN",
    },
    {
        "code": "984",
        "name": "Terres australes et antarctiques françaises",
        "normalized_name": "TERRES AUSTRALES ET ANTARCTIQUES FRANCAISES",
    },
    {
        "code": "986",
        "name": "Wallis-et-Futuna",
        "normalized_name": "WALLIS ET FUTUNA",
    },
    {
        "code": "987",
        "name": "Polynésie française",
        "normalized_name": "POLYNESIE FRANCAISE",
    },
    {
        "code": "988",
        "name": "Nouvelle-Calédonie",
        "normalized_name": "NOUVELLE CALEDONIE",
    },
    {
        "code": "989",
        "name": "Île de Clipperton",
        "normalized_name": "ILE DE CLIPPERTON",
    },
]


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

    def _create_overseas_departments(self) -> None:
        for overseas_department in OVERSEAS_DEPARTMENTS:
            Department.objects.update_or_create(
                code=overseas_department["code"],
                defaults={
                    "name": overseas_department["name"],
                    "normalized_name": overseas_department["normalized_name"],
                    "region": overseas_department["code"],
                },
            )

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

        if scope in {"departements", "all"}:
            self.stdout.write(self.style.NOTICE("Creating overseas departments..."))
            self._create_overseas_departments()
            self.stdout.write(self.style.SUCCESS("Overseas departments created."))
