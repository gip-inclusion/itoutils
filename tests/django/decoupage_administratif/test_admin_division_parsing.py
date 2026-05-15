import pytest
from django.contrib.gis.geos import Point

from itoutils.django.decoupage_administratif.admin_division_parsing import (
    are_department_codes,
    get_division_info_for_division_code,
    get_division_label,
    get_region_if_all_department_codes_belong_to_it,
)
from itoutils.django.decoupage_administratif.constants import WGS84
from itoutils.django.decoupage_administratif.models import EPCI, AdminDivisionType, City, Department, Region

EMPTY_INFO = {"code": None, "label": "", "type": {"value": None, "label": ""}}
FRANCE_INFO = {
    "code": None,
    "label": "France entière",
    "type": {"value": AdminDivisionType.COUNTRY.value, "label": AdminDivisionType.COUNTRY.label},
}


@pytest.mark.parametrize(
    "codes, expected",
    [
        pytest.param({"75"}, True, id="two_digit_numeric"),
        pytest.param({"2A"}, True, id="two_char_alphanumeric"),
        pytest.param({"971"}, True, id="three_digit_numeric"),
        pytest.param({"75", "77", "78"}, True, id="multiple_valid"),
        pytest.param(set(), True, id="empty_set"),  # all() on empty iterable is True
        pytest.param({"75056"}, False, id="city_code_too_long"),
        pytest.param({"200054781"}, False, id="epci_code_too_long"),
        pytest.param({"75", "75056"}, False, id="mixed_valid_and_invalid"),
    ],
)
def test_are_department_codes(codes, expected):
    assert are_department_codes(codes) == expected


@pytest.mark.parametrize(
    "division_code, expected",
    [
        pytest.param("france", FRANCE_INFO, id="literal_france"),
        pytest.param("99100", FRANCE_INFO, id="insee_france"),
        pytest.param(
            "99001",
            {
                "code": None,
                "label": "Pays étranger",
                "type": {"value": AdminDivisionType.COUNTRY.value, "label": AdminDivisionType.COUNTRY.label},
            },
            id="foreign_country",
        ),
        pytest.param("unknown", EMPTY_INFO, id="unknown_code"),
        pytest.param(
            "75056",
            {
                "code": "75056",
                "label": "Paris (75)",
                "type": {"value": AdminDivisionType.CITY.value, "label": AdminDivisionType.CITY.label},
            },
            id="city_found",
        ),
        pytest.param("99999", EMPTY_INFO, id="city_not_found"),
        pytest.param(
            "75",
            {
                "code": "75",
                "label": "Paris",
                "type": {"value": AdminDivisionType.DEPARTMENT.value, "label": AdminDivisionType.DEPARTMENT.label},
            },
            id="department_found",
        ),
        pytest.param("99", EMPTY_INFO, id="department_not_found"),
        pytest.param(
            "200054781",
            {
                "code": "200054781",
                "label": "Métropole du Grand Paris",
                "type": {"value": AdminDivisionType.EPCI.value, "label": AdminDivisionType.EPCI.label},
            },
            id="epci_found",
        ),
        pytest.param("999999999", EMPTY_INFO, id="epci_not_found"),
    ],
)
@pytest.mark.django_db
def test_get_division_info_for_division_code(division_code, expected):
    City.objects.create(
        code="75056",
        name="Paris",
        department="75",
        epci="200054781",
        region="11",
        postal_codes=["75001"],
        center=Point(2.347, 48.8589, srid=WGS84),
    )
    Department.objects.create(code="75", name="Paris", region="11")
    EPCI.objects.create(
        code="200054781",
        name="Métropole du Grand Paris",
        departments=["75", "77", "78", "91", "92", "93", "94", "95"],
        regions=["11"],
    )

    assert get_division_info_for_division_code(division_code) == expected


@pytest.mark.parametrize(
    "department_codes, expected_region_name",
    [
        pytest.param([], None, id="empty_list"),
        pytest.param(["75056"], None, id="city_code_format"),
        pytest.param(["200054781"], None, id="epci_code_format"),
        pytest.param(["75", "99"], None, id="one_dept_not_in_db"),
        pytest.param(["75", "77"], None, id="partial_region"),
        pytest.param(["75", "2A"], None, id="multiple_regions"),
        pytest.param(["A1", "A2"], None, id="region_object_missing"),
        pytest.param(["75", "77", "78", "91", "92", "93", "94", "95"], "Île-de-France", id="all_depts_ile_de_france"),
        pytest.param(
            ["95", "94", "93", "92", "91", "78", "77", "75"], "Île-de-France", id="all_depts_different_order"
        ),
        pytest.param(["2A", "2B"], "Corse", id="all_depts_corse"),
    ],
)
@pytest.mark.django_db
def test_get_region_if_all_department_codes_belong_to_it(department_codes, expected_region_name):
    Region.objects.create(code="11", name="Île-de-France")
    Region.objects.create(code="94", name="Corse")
    Department.objects.create(code="75", name="Paris", region="11")
    Department.objects.create(code="77", name="Seine-et-Marne", region="11")
    Department.objects.create(code="78", name="Yvelines", region="11")
    Department.objects.create(code="91", name="Essonne", region="11")
    Department.objects.create(code="92", name="Hauts-de-Seine", region="11")
    Department.objects.create(code="93", name="Seine-Saint-Denis", region="11")
    Department.objects.create(code="94", name="Val-de-Marne", region="11")
    Department.objects.create(code="95", name="Val-d'Oise", region="11")
    Department.objects.create(code="2A", name="Corse-du-Sud", region="94")
    Department.objects.create(code="2B", name="Haute-Corse", region="94")
    # Départements pointant vers une région inexistante en base
    Department.objects.create(code="A1", name="Dept A1", region="XX")
    Department.objects.create(code="A2", name="Dept A2", region="XX")

    result = get_region_if_all_department_codes_belong_to_it(department_codes)
    assert (result.name if result else None) == expected_region_name


@pytest.mark.parametrize(
    "zone_codes, expected",
    [
        # Entrées invalides
        pytest.param(None, "", id="none"),
        pytest.param([], "", id="empty_list"),
        pytest.param(["unknown"], "", id="unknown_code"),
        # Codes pays
        pytest.param(["france"], "France entière", id="literal_france"),
        pytest.param(["99100"], "France entière", id="insee_france"),
        pytest.param(["99001"], "Pays étranger", id="foreign_country"),
        # Code unique — non trouvé
        pytest.param(["99999"], "", id="city_not_found"),
        pytest.param(["99"], "", id="department_not_found"),
        pytest.param(["999999999"], "", id="epci_not_found"),
        # Code unique — trouvé
        pytest.param(["75056"], "Paris (75)", id="city"),
        pytest.param(["75"], "Paris", id="department_numeric"),
        pytest.param(["2A"], "Corse-du-Sud", id="department_alphanumeric"),
        pytest.param(["971"], "Guadeloupe", id="department_three_digits"),
        pytest.param(["200054781"], "Métropole du Grand Paris", id="epci"),
        # Codes multiples
        pytest.param(["75056", "13001"], "Paris (75), Aix-en-Provence (13)", id="two_cities"),
        pytest.param(["75056", "99999", "13001"], "Paris (75), Aix-en-Provence (13)", id="unknown_code_filtered_out"),
        pytest.param(["99999", "88888"], "", id="multiple_all_not_found"),
        pytest.param(["75", "77", "78", "91", "92", "93", "94", "95"], "Île-de-France", id="all_depts_of_region"),
        pytest.param(
            ["95", "94", "93", "92", "91", "78", "77", "75"], "Île-de-France", id="all_depts_different_order"
        ),
        pytest.param(["75", "77"], "Paris, Seine-et-Marne", id="partial_region"),
        pytest.param(["75", "2A"], "Paris, Corse-du-Sud", id="departments_from_multiple_regions"),
        pytest.param(["2A", "2B"], "Corse", id="all_depts_corse"),
    ],
)
@pytest.mark.django_db
def test_get_division_label(zone_codes, expected):
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
    EPCI.objects.create(
        code="200054781",
        name="Métropole du Grand Paris",
        departments=["75", "77", "78", "91", "92", "93", "94", "95"],
        regions=["11"],
    )
    Region.objects.create(code="11", name="Île-de-France")
    Region.objects.create(code="94", name="Corse")
    Department.objects.create(code="75", name="Paris", region="11")
    Department.objects.create(code="77", name="Seine-et-Marne", region="11")
    Department.objects.create(code="78", name="Yvelines", region="11")
    Department.objects.create(code="91", name="Essonne", region="11")
    Department.objects.create(code="92", name="Hauts-de-Seine", region="11")
    Department.objects.create(code="93", name="Seine-Saint-Denis", region="11")
    Department.objects.create(code="94", name="Val-de-Marne", region="11")
    Department.objects.create(code="95", name="Val-d'Oise", region="11")
    Department.objects.create(code="2A", name="Corse-du-Sud", region="94")
    Department.objects.create(code="2B", name="Haute-Corse", region="94")
    Department.objects.create(code="971", name="Guadeloupe", region="01")

    assert get_division_label(zone_codes) == expected
