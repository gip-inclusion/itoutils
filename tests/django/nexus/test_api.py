import json

import httpx
import pytest

from itoutils.django.nexus.api import NexusAPIClient, NexusAPIException
from itoutils.pytest import nexus_url


class TestClient:
    @pytest.fixture(autouse=True)
    def setup_method(self, mock_nexus_api):
        self.client = NexusAPIClient()
        self.dummy_send_payload = {"key": "value"}
        self.dummy_pks = ["a", "b"]
        self.dummy_pks_payload = [{"id": "a"}, {"id": "b"}]

    def test_init_full_sync(self, mock_nexus_api):
        self.client.init_full_sync()
        [call] = mock_nexus_api.calls
        assert call.request.method == "POST"
        assert call.request.url == "http://nexus/api/sync-start"

    def test_complete_full_sync(self, mock_nexus_api):
        started_at = self.client.init_full_sync()
        mock_nexus_api.reset()

        self.client.complete_full_sync(started_at)
        [call] = mock_nexus_api.calls
        assert call.request.method == "POST"
        assert call.request.url == "http://nexus/api/sync-completed"
        assert json.loads(call.request.content.decode()) == {"started_at": started_at}

    def test_send_users(self, mock_nexus_api):
        self.client.send_users(self.dummy_send_payload)
        [call] = mock_nexus_api.calls
        assert call.request.method == "POST"
        assert call.request.url == "http://nexus/api/users"
        assert json.loads(call.request.content.decode()) == self.dummy_send_payload

    def test_delete_users(self, mock_nexus_api):
        self.client.delete_users(self.dummy_pks)
        [call] = mock_nexus_api.calls
        assert call.request.method == "DELETE"
        assert call.request.url == "http://nexus/api/users"
        assert json.loads(call.request.content.decode()) == self.dummy_pks_payload

    def test_send_structures(self, mock_nexus_api):
        self.client.send_structures(self.dummy_send_payload)
        [call] = mock_nexus_api.calls
        assert call.request.method == "POST"
        assert call.request.url == "http://nexus/api/structures"
        assert json.loads(call.request.content.decode()) == self.dummy_send_payload

    def test_delete_structures(self, mock_nexus_api):
        self.client.delete_structures(self.dummy_pks)
        [call] = mock_nexus_api.calls
        assert call.request.method == "DELETE"
        assert call.request.url == "http://nexus/api/structures"
        assert json.loads(call.request.content.decode()) == self.dummy_pks_payload

    def test_send_memberships(self, mock_nexus_api):
        self.client.send_memberships(self.dummy_send_payload)
        [call] = mock_nexus_api.calls
        assert call.request.method == "POST"
        assert call.request.url == "http://nexus/api/memberships"
        assert json.loads(call.request.content.decode()) == self.dummy_send_payload

    def test_delete_memberships(self, mock_nexus_api):
        self.client.delete_memberships(self.dummy_pks)
        [call] = mock_nexus_api.calls
        assert call.request.method == "DELETE"
        assert call.request.url == "http://nexus/api/memberships"
        assert json.loads(call.request.content.decode()) == self.dummy_pks_payload

    def test_dropdown_status(self, mock_nexus_api):
        self.client.dropdown_status("email@mailinator.com")
        [call] = mock_nexus_api.calls
        assert call.request.method == "POST"
        assert call.request.url == "http://nexus/api/dropdown-status"
        assert json.loads(call.request.content.decode()) == {"email": "email@mailinator.com"}

    def test_200_with_errors(self, mock_nexus_api, caplog):
        mock_nexus_api.post(nexus_url("structures")).respond(
            200, json={"errors": {"my-id": {"post_code": ["Ce champ ne peut être vide."]}}}
        )
        self.client.send_structures(self.dummy_send_payload)
        assert caplog.messages == [
            'HTTP Request: POST http://nexus/api/structures "HTTP/1.1 200 OK"',
            "nexus POST:structures error={'my-id': {'post_code': ['Ce champ ne peut être vide.']}}",
        ]

    def test_400(self, mock_nexus_api, caplog):
        mock_nexus_api.post(nexus_url("sync-completed")).respond(
            400, json={"errors": {"started_at": ["Ce champ est obligatoire."]}}
        )
        with pytest.raises(NexusAPIException):
            self.client.complete_full_sync("bad start_at")
        assert caplog.messages == [
            'HTTP Request: POST http://nexus/api/sync-completed "HTTP/1.1 400 Bad Request"',
            "nexus POST:sync-completed error={'errors': {'started_at': ['Ce champ est obligatoire.']}}",
        ]

    def test_503(self, mock_nexus_api, caplog):
        mock_nexus_api.post(nexus_url("sync-completed")).respond(503)
        with pytest.raises(NexusAPIException):
            self.client.complete_full_sync("bad start_at")
        assert caplog.messages == [
            'HTTP Request: POST http://nexus/api/sync-completed "HTTP/1.1 503 Service Unavailable"',
            "nexus POST:sync-completed error=Server error '503 Service Unavailable' "
            "for url 'http://nexus/api/sync-completed'\n"
            "For more information check: "
            "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/503",
        ]

    def test_connexion_refused(self, mock_nexus_api, caplog):
        mock_nexus_api.post(nexus_url("structures")).mock(
            side_effect=httpx.ConnectError(message="[Errno 111] Connection refused")
        )
        with pytest.raises(NexusAPIException):
            self.client.send_structures(self.dummy_send_payload)
        assert caplog.messages == [
            "nexus POST:structures error=[Errno 111] Connection refused",
        ]
