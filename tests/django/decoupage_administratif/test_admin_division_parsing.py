import pytest
from django.contrib.gis.geos import Point

from itoutils.django.decoupage_administratif.admin_division_parsing import get_division_info
from itoutils.django.decoupage_administratif.constants import WGS84
from itoutils.django.decoupage_administratif.models import EPCI, AdminDivisionType, City, Department, Region


def test_get_division_info_france():
    assert get_division_info(["france"]) == {
        "code": None,
        "label": "France entière",
        "type": {
            "value": AdminDivisionType.COUNTRY.value,
            "label": AdminDivisionType.COUNTRY.label,
        },
    }


@pytest.mark.django_db
def test_get_division_info_city():
    City.objects.create(
        code="75056",
        name="Paris",
        department="75",
        epci="200054781",
        region="11",
        postal_codes=["75001"],
        center=Point(2.347, 48.8589, srid=WGS84),
    )

    result = get_division_info(["75056"])
    assert result == {
        "code": "75056",
        "label": "Paris (75)",
        "type": {
            "value": AdminDivisionType.CITY.value,
            "label": AdminDivisionType.CITY.label,
        },
    }


@pytest.mark.django_db
def test_get_division_info_city_not_found():
    result = get_division_info(["99999"])
    assert result == {
        "code": None,
        "label": "",
        "type": {
            "value": None,
            "label": "",
        },
    }


@pytest.mark.django_db
def test_get_division_info_department():
    Department.objects.create(code="75", name="Paris", region="11")

    result = get_division_info(["75"])
    assert result == {
        "code": "75",
        "label": "Paris",
        "type": {
            "value": AdminDivisionType.DEPARTMENT.value,
            "label": AdminDivisionType.DEPARTMENT.label,
        },
    }


@pytest.mark.django_db
def test_get_division_info_department_with_letter():
    Department.objects.create(code="2A", name="Corse-du-Sud", region="94")

    result = get_division_info(["2A"])
    assert result == {
        "code": "2A",
        "label": "Corse-du-Sud",
        "type": {
            "value": AdminDivisionType.DEPARTMENT.value,
            "label": AdminDivisionType.DEPARTMENT.label,
        },
    }


@pytest.mark.django_db
def test_get_division_info_department_not_found():
    result = get_division_info(["99"])
    assert result == {
        "code": None,
        "label": "",
        "type": {
            "value": None,
            "label": "",
        },
    }


@pytest.mark.django_db
def test_get_division_info_epci():
    EPCI.objects.create(
        code="200054781",
        name="Métropole du Grand Paris",
        departments=["75", "77", "78", "91", "92", "93", "94", "95"],
        regions=["11"],
    )

    result = get_division_info(["200054781"])
    assert result == {
        "code": "200054781",
        "label": "Métropole du Grand Paris",
        "type": {
            "value": AdminDivisionType.EPCI.value,
            "label": AdminDivisionType.EPCI.label,
        },
    }


@pytest.mark.django_db
def test_get_division_info_epci_not_found():
    result = get_division_info(["999999999"])
    assert result == {
        "code": None,
        "label": "",
        "type": {
            "value": None,
            "label": "",
        },
    }


def test_get_division_info_country_france():
    result = get_division_info(["99100"])
    assert result == {
        "code": None,
        "label": "France entière",
        "type": {
            "value": AdminDivisionType.COUNTRY.value,
            "label": AdminDivisionType.COUNTRY.label,
        },
    }


def test_get_division_info_country_other():
    result = get_division_info(["99001"])
    assert result == {
        "code": None,
        "label": "",
        "type": {
            "value": None,
            "label": "",
        },
    }


def test_get_division_info_unknown():
    result = get_division_info(["unknown"])
    assert result == {
        "code": None,
        "label": "",
        "type": {
            "value": None,
            "label": "",
        },
    }


@pytest.mark.django_db
def test_get_division_info_region():
    Region.objects.create(code="11", name="Île-de-France")
    Department.objects.create(code="75", name="Paris", region="11")
    Department.objects.create(code="77", name="Seine-et-Marne", region="11")
    Department.objects.create(code="78", name="Yvelines", region="11")
    Department.objects.create(code="91", name="Essonne", region="11")
    Department.objects.create(code="92", name="Hauts-de-Seine", region="11")
    Department.objects.create(code="93", name="Seine-Saint-Denis", region="11")
    Department.objects.create(code="94", name="Val-de-Marne", region="11")
    Department.objects.create(code="95", name="Val-d'Oise", region="11")

    zone_codes = ["75", "77", "78", "91", "92", "93", "94", "95"]
    result = get_division_info(zone_codes)
    assert result == {
        "code": None,
        "label": "Île-de-France",
        "type": {
            "value": AdminDivisionType.REGION.value,
            "label": AdminDivisionType.REGION.label,
        },
    }


@pytest.mark.django_db
def test_get_division_info_region_different_order():
    Region.objects.create(code="11", name="Île-de-France")
    Department.objects.create(code="75", name="Paris", region="11")
    Department.objects.create(code="77", name="Seine-et-Marne", region="11")
    Department.objects.create(code="78", name="Yvelines", region="11")
    Department.objects.create(code="91", name="Essonne", region="11")
    Department.objects.create(code="92", name="Hauts-de-Seine", region="11")
    Department.objects.create(code="93", name="Seine-Saint-Denis", region="11")
    Department.objects.create(code="94", name="Val-de-Marne", region="11")
    Department.objects.create(code="95", name="Val-d'Oise", region="11")

    zone_codes = ["95", "94", "93", "92", "91", "78", "77", "75"]
    result = get_division_info(zone_codes)
    assert result == {
        "code": None,
        "label": "Île-de-France",
        "type": {
            "value": AdminDivisionType.REGION.value,
            "label": AdminDivisionType.REGION.label,
        },
    }


@pytest.mark.django_db
def test_get_division_info_region_partial():
    Region.objects.create(code="11", name="Île-de-France")
    Department.objects.create(code="75", name="Paris", region="11")
    Department.objects.create(code="77", name="Seine-et-Marne", region="11")
    Department.objects.create(code="78", name="Yvelines", region="11")
    Department.objects.create(code="91", name="Essonne", region="11")
    Department.objects.create(code="92", name="Hauts-de-Seine", region="11")
    Department.objects.create(code="93", name="Seine-Saint-Denis", region="11")
    Department.objects.create(code="94", name="Val-de-Marne", region="11")
    Department.objects.create(code="95", name="Val-d'Oise", region="11")

    zone_codes = ["75", "77"]
    result = get_division_info(zone_codes)
    assert result == {
        "code": None,
        "label": "Paris, Seine-et-Marne",
        "type": {
            "value": None,
            "label": "",
        },
    }


@pytest.mark.django_db
def test_get_division_info_multiple_codes():
    City.objects.create(
        code="75056",
        name="Paris",
        department="75",
        epci="200054781",
        region="11",
        postal_codes=["75001"],
        center=Point(2.347, 48.8589, srid=WGS84),
    )
    City.objects.create(
        code="13001",
        name="Aix-en-Provence",
        department="13",
        epci="200054781",
        region="93",
        postal_codes=["13100"],
        center=Point(4.8357, 45.7640, srid=WGS84),
    )

    zone_codes = ["75056", "13001"]
    result = get_division_info(zone_codes)
    assert result == {
        "code": None,
        "label": "Paris (75), Aix-en-Provence (13)",
        "type": {
            "value": None,
            "label": "",
        },
    }


@pytest.mark.django_db
def test_get_division_info_with_empty_display():
    City.objects.create(
        code="75056",
        name="Paris",
        department="75",
        epci="200054781",
        region="11",
        postal_codes=["75001"],
        center=Point(2.347, 48.8589, srid=WGS84),
    )
    City.objects.create(
        code="13001",
        name="Aix-en-Provence",
        department="13",
        epci="200054781",
        region="93",
        postal_codes=["13100"],
        center=Point(4.8357, 45.7640, srid=WGS84),
    )

    zone_codes = ["75056", "99999", "13001"]
    result = get_division_info(zone_codes)
    assert result == {
        "code": None,
        "label": "Paris (75), Aix-en-Provence (13)",
        "type": {
            "value": None,
            "label": "",
        },
    }


@pytest.mark.django_db
def test_get_division_info_all_empty():
    zone_codes = ["99999", "88888"]
    result = get_division_info(zone_codes)
    assert result == {
        "code": None,
        "label": "",
        "type": {
            "value": None,
            "label": "",
        },
    }


@pytest.mark.django_db
def test_get_division_info_guadeloupe():
    Department.objects.create(code="971", name="Guadeloupe", region="01")

    zone_codes = ["971"]
    result = get_division_info(zone_codes)
    assert result == {
        "code": "971",
        "label": "Guadeloupe",
        "type": {
            "value": AdminDivisionType.DEPARTMENT.value,
            "label": AdminDivisionType.DEPARTMENT.label,
        },
    }


@pytest.mark.django_db
def test_get_division_info_corse():
    Region.objects.create(code="94", name="Corse")
    Department.objects.create(code="2A", name="Corse-du-Sud", region="94")
    Department.objects.create(code="2B", name="Haute-Corse", region="94")

    zone_codes = ["2A", "2B"]
    result = get_division_info(zone_codes)
    assert result == {
        "code": None,
        "label": "Corse",
        "type": {
            "value": AdminDivisionType.REGION.value,
            "label": AdminDivisionType.REGION.label,
        },
    }
