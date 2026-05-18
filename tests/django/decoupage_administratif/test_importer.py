from unittest import mock

import pytest

from itoutils.django.decoupage_administratif.importer import (
    DecoupageAdministratifImporter,
)
from itoutils.django.decoupage_administratif.models import (
    EPCI,
    City,
    Department,
    Region,
)


@pytest.fixture
def client():
    return mock.Mock()


@pytest.fixture
def importer(client):
    return DecoupageAdministratifImporter(client=client)


@pytest.mark.parametrize(
    ("model", "fetch_method", "import_method", "code", "first_name", "second_name"),
    [
        pytest.param(
            Region,
            "fetch_regions",
            "import_regions",
            "44",
            "Petit Est",
            "Grand Est",
            id="region",
        ),
        pytest.param(
            Department,
            "fetch_departements",
            "import_departements",
            "75",
            "Île-de-France",
            "Paris",
            id="department",
        ),
        pytest.param(
            EPCI,
            "fetch_epci",
            "import_epci",
            "200054781",
            "Grand Paris",
            "Métropole du Grand Paris",
            id="epci",
        ),
        pytest.param(
            City,
            "fetch_communes",
            "import_communes",
            "75056",
            "Ville de Paris",
            "Paris",
            id="commune",
        ),
        pytest.param(
            City,
            "fetch_arrondissements",
            "import_arrondissements",
            "75101",
            "Paris 1",
            "Paris 1er Arrondissement",
            id="arrondissement",
        ),
    ],
)
@pytest.mark.django_db
def test_import_create_and_update(
    client,
    importer,
    model,
    fetch_method,
    import_method,
    code,
    first_name,
    second_name,
):
    assert model.objects.count() == 0

    # Création
    record = {"code": code, "nom": first_name}
    if model is City:
        record["codeDepartement"] = "74"
    if model is Department:
        record["codeRegion"] = "10"
    getattr(client, fetch_method).return_value = [record]
    getattr(importer, import_method)()
    assert model.objects.count() == 1
    instance = model.objects.get(code=code)
    assert instance.name == first_name
    if model is Department:
        assert instance.region == "10"

    # Mise à jour
    record["nom"] = second_name
    if model is City:
        record["codeDepartement"] = "75"
    if model is Department:
        record["codeRegion"] = "11"
    getattr(importer, import_method)()
    assert model.objects.count() == 1
    instance = model.objects.get(code=code)
    assert instance.name == second_name
    if model is Department:
        assert instance.region == "11"


@pytest.mark.django_db
def test_import_departements_sets_region_codes(client, importer):
    Region.objects.create(code="11", name="Île-de-France")
    client.fetch_departements.return_value = [
        {"code": "75", "nom": "Paris", "codeRegion": "11"},
    ]

    importer.import_departements()

    department = Department.objects.get(code="75")
    assert department.name == "Paris"
    assert department.region == "11"


@pytest.mark.django_db
def test_import_arrondissements_creates_city(client, importer):
    client.fetch_arrondissements.return_value = [
        {
            "code": "75101",
            "nom": "Paris 1er Arrondissement",
        }
    ]

    importer.import_arrondissements()

    city = City.objects.get(code="75101")
    assert city.name == "Paris 1er Arrondissement"


def test_import_all_runs_every_step(importer):
    with (
        mock.patch.object(importer, "import_regions") as import_regions,
        mock.patch.object(importer, "import_departements") as import_departements,
        mock.patch.object(importer, "import_epci") as import_epci,
        mock.patch.object(importer, "import_communes") as import_communes,
        mock.patch.object(importer, "import_arrondissements") as import_arrondissements,
    ):
        importer.import_all()

    import_regions.assert_called_once_with()
    import_departements.assert_called_once_with()
    import_epci.assert_called_once_with()
    import_communes.assert_called_once_with()
    import_arrondissements.assert_called_once_with()
