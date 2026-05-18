import io

import pytest
from django.core.management import call_command

from itoutils.django.decoupage_administratif.management.commands.import_decoupage_administratif import (
    OVERSEAS_DEPARTMENTS,
)
from itoutils.django.decoupage_administratif.models import Department

IMPORTER_PATH = (
    "itoutils.django.decoupage_administratif.management.commands"
    ".import_decoupage_administratif.DecoupageAdministratifImporter"
)

SCOPES_AND_METHODS = [
    ("regions", "import_regions"),
    ("departements", "import_departements"),
    ("epci", "import_epci"),
    ("communes", "import_communes"),
    ("arrondissements", "import_arrondissements"),
    ("all", "import_all"),
]


@pytest.mark.django_db
def test_command_runs_full_import_by_default(mocker):
    importer_cls = mocker.patch(IMPORTER_PATH)

    call_command("import_decoupage_administratif")

    importer_cls.return_value.import_all.assert_called_once_with()


@pytest.mark.django_db
@pytest.mark.parametrize("scope,method_name", SCOPES_AND_METHODS)
def test_command_supports_scope_argument(mocker, scope, method_name):
    importer_cls = mocker.patch(IMPORTER_PATH)
    importer_instance = importer_cls.return_value

    call_command("import_decoupage_administratif", scope=scope)

    getattr(importer_instance, method_name).assert_called_once_with()
    for other_method_name in dict(SCOPES_AND_METHODS).values():
        if other_method_name != method_name:
            getattr(importer_instance, other_method_name).assert_not_called()


@pytest.mark.django_db
def test_command_prints_progress_messages(mocker):
    mocker.patch(IMPORTER_PATH)
    out = io.StringIO()

    call_command("import_decoupage_administratif", stdout=out)

    output = out.getvalue()
    assert "Starting import 'all'..." in output
    assert "Import completed." in output


@pytest.mark.django_db
@pytest.mark.parametrize(
    "scope,expected_count",
    [
        ("regions", 0),
        ("epci", 0),
        ("communes", 0),
        ("arrondissements", 0),
        ("departements", len(OVERSEAS_DEPARTMENTS)),
        ("all", len(OVERSEAS_DEPARTMENTS)),
    ],
)
def test_command_creates_overseas_departments_only_for_all_or_departements(mocker, scope, expected_count):
    mocker.patch(IMPORTER_PATH)

    call_command("import_decoupage_administratif", scope=scope, wet_run=True)

    assert Department.objects.count() == expected_count
    if expected_count:
        for overseas_department in OVERSEAS_DEPARTMENTS:
            department = Department.objects.get(code=overseas_department["code"])
            assert department.name == overseas_department["name"]
            assert department.region == overseas_department["code"]
