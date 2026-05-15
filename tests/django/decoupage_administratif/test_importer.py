from unittest import mock

import pytest

from itoutils.django.decoupage_administratif.importer import (
    DecoupageAdministratifImporter,
    _parse_center,
)
from itoutils.django.decoupage_administratif.models import EPCI, City, Department, Region


@pytest.fixture
def client():
    return mock.Mock()


@pytest.fixture
def importer(client):
    return DecoupageAdministratifImporter(client=client)


def test_import_regions_updates_names(db, client, importer):
    Region.objects.create(code="44", name="Old Name")
    client.fetch_regions.return_value = [
        {"code": "44", "nom": "Grand Est"},
        {"code": "01", "nom": "Guadeloupe"},
    ]

    importer.import_regions()

    assert Region.objects.count() == 2
    assert Region.objects.get(code="44").name == "Grand Est"
    assert Region.objects.get(code="01").name == "Guadeloupe"


def test_import_regions_sets_normalized_name(db, client, importer):
    client.fetch_regions.return_value = [
        {"code": "44", "nom": "Grand Est"},
    ]

    importer.import_regions()

    assert Region.objects.get(code="44").normalized_name == "GRAND EST"


def test_import_departements_sets_region_codes(db, client, importer):
    Region.objects.create(code="11", name="Île-de-France")
    client.fetch_departements.return_value = [
        {"code": "75", "nom": "Paris", "codeRegion": "11"},
    ]

    importer.import_departements()

    department = Department.objects.get(code="75")
    assert department.name == "Paris"
    assert department.region == "11"


def test_import_departements_sets_normalized_name(db, client, importer):
    client.fetch_departements.return_value = [
        {"code": "75", "nom": "Paris", "codeRegion": "11"},
    ]

    importer.import_departements()

    assert Department.objects.get(code="75").normalized_name == "PARIS"


def test_import_epci_defaults_empty_lists(db, client, importer):
    client.fetch_epci.return_value = [
        {
            "code": "200069193",
            "nom": "Métropole de Lyon",
            # intentionally missing optional fields
        }
    ]

    importer.import_epci()

    epci = EPCI.objects.get(code="200069193")
    assert epci.departments == []
    assert epci.regions == []


def test_import_epci_sets_normalized_name(db, client, importer):
    client.fetch_epci.return_value = [
        {
            "code": "200054781",
            "nom": "Métropole du Grand Paris",
            "codesDepartements": ["75"],
            "codesRegions": ["11"],
        }
    ]

    importer.import_epci()

    assert EPCI.objects.get(code="200054781").normalized_name == "METROPOLE DU GRAND PARIS"


def test_import_communes_handles_missing_values(db, client, importer):
    client.fetch_communes.return_value = [
        {
            "code": "75056",
            "nom": "Paris",
            "codesPostaux": ["75001"],
            "centre": {"type": "Point", "coordinates": [2.347, 48.8589]},
        }
    ]

    importer.import_communes()

    city = City.objects.get(code="75056")
    assert city.department == ""
    assert city.epci == ""
    assert city.region == ""
    assert city.postal_codes == ["75001"]
    assert city.population is None
    assert city.center is not None
    assert city.center.x == pytest.approx(2.347, abs=1e-3)
    assert city.center.y == pytest.approx(48.8589, abs=1e-3)


def test_import_communes_sets_population_and_center(db, client, importer):
    client.fetch_communes.return_value = [
        {
            "code": "75056",
            "nom": "Paris",
            "codeDepartement": "75",
            "codeRegion": "11",
            "codeEpci": "200054781",
            "codesPostaux": ["75001"],
            "population": 2161000,
            "centre": {"type": "Point", "coordinates": [2.347, 48.8589]},
        }
    ]

    importer.import_communes()

    city = City.objects.get(code="75056")
    assert city.population == 2161000
    assert city.center is not None
    assert city.center.x == pytest.approx(2.347, abs=1e-3)
    assert city.center.y == pytest.approx(48.8589, abs=1e-3)


def test_import_communes_sets_normalized_name_with_department(db, client, importer):
    client.fetch_communes.return_value = [
        {
            "code": "75056",
            "nom": "Paris",
            "codeDepartement": "75",
            "codeRegion": "11",
            "codesPostaux": ["75001"],
            "centre": {"type": "Point", "coordinates": [2.347, 48.8589]},
        }
    ]

    importer.import_communes()

    city = City.objects.get(code="75056")
    assert "PARIS" in city.normalized_name
    assert "75" in city.normalized_name


def test_import_arrondissements_creates_city(db, client, importer):
    client.fetch_arrondissements.return_value = [
        {
            "code": "75101",
            "nom": "Paris 1er Arrondissement",
            "codeDepartement": "75",
            "codeRegion": "11",
            "codesPostaux": ["75001"],
            "population": 15114,
            "centre": {"type": "Point", "coordinates": [2.347, 48.8589]},
        }
    ]

    importer.import_arrondissements()

    city = City.objects.get(code="75101")
    assert city.name == "Paris 1er Arrondissement"
    assert city.department == "75"
    assert city.region == "11"
    assert city.epci == ""
    assert city.postal_codes == ["75001"]
    assert city.population == 15114
    assert city.center is not None
    assert city.center.x == pytest.approx(2.347, abs=1e-3)
    assert city.center.y == pytest.approx(48.8589, abs=1e-3)


def test_import_arrondissements_sets_normalized_name_with_department(db, client, importer):
    client.fetch_arrondissements.return_value = [
        {
            "code": "13201",
            "nom": "Marseille 1er Arrondissement",
            "codeDepartement": "13",
            "codeRegion": "93",
            "codesPostaux": ["13001"],
            "centre": {"type": "Point", "coordinates": [5.3698, 43.2965]},
        }
    ]

    importer.import_arrondissements()

    city = City.objects.get(code="13201")
    assert "MARSEILLE 1ER ARRONDISSEMENT" in city.normalized_name
    assert "13" in city.normalized_name


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


def test_parse_center_with_valid_point():
    result = _parse_center({"type": "Point", "coordinates": [2.347, 48.8589]})

    assert result is not None
    assert result.x == pytest.approx(2.347, abs=1e-3)
    assert result.y == pytest.approx(48.8589, abs=1e-3)


def test_parse_center_with_none():
    assert _parse_center(None) is None


def test_parse_center_with_empty_dict():
    assert _parse_center({}) is None


def test_parse_center_with_wrong_type():
    assert _parse_center({"type": "Polygon", "coordinates": [[0, 0], [1, 1]]}) is None


def test_parse_center_with_missing_coordinates():
    assert _parse_center({"type": "Point"}) is None


def test_parse_center_with_invalid_coordinates():
    assert _parse_center({"type": "Point", "coordinates": [2.347]}) is None
