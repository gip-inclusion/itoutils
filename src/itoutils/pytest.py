import contextlib
import io
import logging
from unittest import mock
from urllib.parse import urljoin

import pytest
from django.conf import settings as django_settings
from django.utils import timezone


@pytest.fixture
def capture_stream_handler_log(request):
    # Workaround capsys/capfd not working, see https://github.com/pytest-dev/pytest/issues/5997
    @contextlib.contextmanager
    def capture_stream_handler(logger):
        with contextlib.ExitStack() as stack:
            captured = io.StringIO()
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    stack.enter_context(mock.patch.object(handler, "stream", captured))
            yield captured

    return capture_stream_handler


@pytest.fixture
def mock_nexus_token():
    with mock.patch("itoutils.django.nexus.views.generate_auto_login_token", return_value="JWT") as mocked:
        yield mocked


def nexus_url(endpoint):
    return urljoin(django_settings.NEXUS_API_BASE_URL, endpoint)


@pytest.fixture
def mock_nexus_api(respx_mock, settings):
    settings.NEXUS_API_BASE_URL = "http://nexus/api/"
    settings.NEXUS_API_TOKEN = "very-secret-token"
    respx_mock.post(nexus_url("sync-start")).respond(200, json={"started_at": timezone.now().isoformat()})
    respx_mock.post(nexus_url("users")).respond(200, json={})
    respx_mock.delete(nexus_url("users")).respond(200, json={})
    respx_mock.post(nexus_url("structures")).respond(200, json={})
    respx_mock.delete(nexus_url("structures")).respond(200, json={})
    respx_mock.post(nexus_url("memberships")).respond(200, json={})
    respx_mock.delete(nexus_url("memberships")).respond(200, json={})
    respx_mock.post(nexus_url("sync-completed")).respond(200, json={})
    return respx_mock
