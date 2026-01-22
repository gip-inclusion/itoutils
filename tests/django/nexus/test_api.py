import json

import pytest

from itoutils.django.nexus.api import NexusAPIClient


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
