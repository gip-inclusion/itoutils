import contextlib
import io
import logging
from unittest import mock

import pytest
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


@pytest.fixture
def mock_nexus_api(respx_mock, settings):
    settings.NEXUS_API_BASE_URL = "http://nexus/api/"
    settings.NEXUS_API_TOKEN = "very-secret-token"
    respx_mock.post(f"{settings.NEXUS_API_BASE_URL}sync-start").respond(
        200, json={"started_at": timezone.now().isoformat()}
    )
    respx_mock.post(f"{settings.NEXUS_API_BASE_URL}users").respond(200)
    respx_mock.delete(f"{settings.NEXUS_API_BASE_URL}users").respond(200)
    respx_mock.post(f"{settings.NEXUS_API_BASE_URL}structures").respond(200)
    respx_mock.delete(f"{settings.NEXUS_API_BASE_URL}structures").respond(200)
    respx_mock.post(f"{settings.NEXUS_API_BASE_URL}memberships").respond(200)
    respx_mock.delete(f"{settings.NEXUS_API_BASE_URL}memberships").respond(200)
    respx_mock.post(f"{settings.NEXUS_API_BASE_URL}sync-completed").respond(200)
    return respx_mock
