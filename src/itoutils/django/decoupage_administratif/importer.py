import logging

from django.db import transaction

from .api_client import DecoupageAdministratifAPIClient
from .models import EPCI, City, Department, Region

logger = logging.getLogger(__name__)


class DecoupageAdministratifImporter:
    """Load data from the API and store it in the database."""

    def __init__(self, client: DecoupageAdministratifAPIClient | None = None) -> None:
        self.client = client or DecoupageAdministratifAPIClient()

    @transaction.atomic
    def import_regions(self) -> None:
        payload = self.client.fetch_regions()
        for region in payload:
            code = region["code"]
            name = region["nom"]

            Region.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                },
            )

    @transaction.atomic
    def import_departements(self) -> None:
        payload = self.client.fetch_departements()
        for dept in payload:
            code = dept["code"]
            name = dept["nom"]
            region = dept["codeRegion"]

            Department.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "region": region,
                },
            )

    @transaction.atomic
    def import_epci(self) -> None:
        payload = self.client.fetch_epci()
        for epci in payload:
            code = epci["code"]
            name = epci["nom"]

            EPCI.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                },
            )

    @transaction.atomic
    def import_communes(self) -> None:
        payload = self.client.fetch_communes()
        for commune in payload:
            code = commune["code"]
            name = commune["nom"]
            department = commune["codeDepartement"]

            City.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "department": department,
                },
            )

    @transaction.atomic
    def import_arrondissements(self) -> None:
        payload = self.client.fetch_arrondissements()
        for arrondissement in payload:
            code = arrondissement["code"]
            name = arrondissement["nom"]

            City.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                },
            )

    def import_all(self) -> None:
        """Import all entities in dependency order."""
        self.import_regions()
        self.import_departements()
        self.import_epci()
        self.import_communes()
        self.import_arrondissements()
