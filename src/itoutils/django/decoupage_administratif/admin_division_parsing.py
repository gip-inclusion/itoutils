import re

from .models import (
    EPCI,
    AdminDivisionType,
    City,
    Department,
    Region,
)

FRANCE_INSEE_CODE = "99100"

COUNTRY_CODE_PATTERN = r"^99[0-5]\d{2}$"
CITY_CODE_PATTERN = r"^\w{5}$"
DEPARTMENT_CODE_PATTERN = r"^\w{2,3}$"
EPCI_CODE_PATTERN = r"^\d{9}$"
REGION_CODE_PATTERN = r"^\w{2}$"


def get_division_info_for_division_code(division_code: str) -> dict:
    if division_code in ["france", FRANCE_INSEE_CODE]:
        return {
            "code": None,
            "label": "France entière",
            "type": {
                "value": AdminDivisionType.COUNTRY.value,
                "label": AdminDivisionType.COUNTRY.label,
            },
        }

    if re.match(COUNTRY_CODE_PATTERN, division_code):
        return {
            "code": None,
            "label": "",
            "type": {
                "value": None,
                "label": "",
            },
        }

    if re.match(CITY_CODE_PATTERN, division_code):
        city = City.objects.filter(code=division_code).first()
        if city:
            return {
                "code": city.code,
                "label": f"{city.name} ({city.department})",
                "type": {
                    "value": AdminDivisionType.CITY.value,
                    "label": AdminDivisionType.CITY.label,
                },
            }

    if re.match(DEPARTMENT_CODE_PATTERN, division_code):
        department = Department.objects.filter(code=division_code).first()
        if department:
            return {
                "code": department.code,
                "label": department.name,
                "type": {
                    "value": AdminDivisionType.DEPARTMENT.value,
                    "label": AdminDivisionType.DEPARTMENT.label,
                },
            }

    if re.match(EPCI_CODE_PATTERN, division_code):
        epci = EPCI.objects.filter(code=division_code).first()
        if epci:
            return {
                "code": epci.code,
                "label": epci.name,
                "type": {
                    "value": AdminDivisionType.EPCI.value,
                    "label": AdminDivisionType.EPCI.label,
                },
            }

    return {
        "code": None,
        "label": "",
        "type": {
            "value": None,
            "label": "",
        },
    }


def are_department_codes(department_codes: set[str]) -> bool:
    # Codes attendus : 2 ou 3 lettres ou chiffres
    return all(re.match(DEPARTMENT_CODE_PATTERN, code) for code in department_codes)


def get_region_if_all_department_codes_belong_to_it(
    department_codes: list[str],
) -> Region | None:
    department_codes = set(department_codes)

    if not department_codes:
        # Liste vide
        return None

    if not are_department_codes(department_codes):
        # Un ou plusieurs codes n'ont pas le format attendu
        return None

    departments = list(Department.objects.filter(code__in=department_codes).values("code", "region"))

    if len(departments) != len(department_codes):
        # Un ou plusieurs codes ne correspondent pas à des départements
        return None

    region_codes = {dept["region"] for dept in departments}

    if len(region_codes) != 1:
        # Les départements ne correspondent pas à une seule région
        return None

    region_code = region_codes.pop()
    region_departments_count = Department.objects.filter(region=region_code).count()

    if region_departments_count != len(department_codes):
        # La région comporte un nombre de départements différent des départements fournis
        return None

    # Tous les départements correspondent à une seule région
    return Region.objects.filter(code=region_code).first()


def get_division_info(division_codes: list[str] | None) -> dict:
    if division_codes is None:
        return {
            "code": None,
            "label": "",
            "type": {
                "value": None,
                "label": "",
            },
        }

    if len(division_codes) == 1:
        return get_division_info_for_division_code(division_codes[0])

    region = get_region_if_all_department_codes_belong_to_it(division_codes)
    if region:
        return {
            "code": None,
            "label": region.name,
            "type": {
                "value": AdminDivisionType.REGION.value,
                "label": AdminDivisionType.REGION.label,
            },
        }

    return {
        "code": None,
        "label": ", ".join(
            [
                division_info["label"]
                for division_code in division_codes
                if (division_info := get_division_info_for_division_code(division_code)) and division_info["label"]
            ]
        ),
        "type": {
            "value": None,
            "label": "",
        },
    }
