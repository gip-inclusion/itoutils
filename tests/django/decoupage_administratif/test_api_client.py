from unittest import mock

import pytest
import requests

from itoutils.django.decoupage_administratif.api_client import DecoupageAdministratifAPIClient


@pytest.fixture
def session():
    s = mock.Mock()
    response = mock.Mock()
    response.json.return_value = [{"code": "dummy"}]
    response.raise_for_status.return_value = None
    s.get.return_value = response
    return s


@pytest.fixture
def api_client(session):
    return DecoupageAdministratifAPIClient(
        base_url="https://example.com",
        timeout_seconds=5,
        session=session,
    )


def test_fetch_communes_calls_expected_endpoint(session, api_client):
    data = api_client.fetch_communes()

    assert data == session.get.return_value.json.return_value
    session.get.assert_called_once_with(
        "https://example.com/communes",
        params={
            "fields": "code,nom,codeDepartement,codeRegion,codesPostaux,codeEpci,population,centre",
            "format": "json",
        },
        timeout=5,
    )


def test_fetch_departements_calls_expected_endpoint(session, api_client):
    data = api_client.fetch_departements()

    assert data == session.get.return_value.json.return_value
    session.get.assert_called_once_with(
        "https://example.com/departements",
        params={"fields": "code,nom,codeRegion", "format": "json"},
        timeout=5,
    )


def test_fetch_epci_calls_expected_endpoint(session, api_client):
    data = api_client.fetch_epci()

    assert data == session.get.return_value.json.return_value
    session.get.assert_called_once_with(
        "https://example.com/epcis",
        params={
            "fields": "code,nom,codesDepartements,codesRegions",
            "format": "json",
        },
        timeout=5,
    )


def test_fetch_regions_calls_expected_endpoint(session, api_client):
    data = api_client.fetch_regions()

    assert data == session.get.return_value.json.return_value
    session.get.assert_called_once_with(
        "https://example.com/regions",
        params={"fields": "code,nom", "format": "json"},
        timeout=5,
    )


def test_fetch_communes_propagates_http_errors(session, api_client):
    session.get.return_value.raise_for_status.side_effect = requests.HTTPError("boom")

    with pytest.raises(requests.HTTPError):
        api_client.fetch_communes()
