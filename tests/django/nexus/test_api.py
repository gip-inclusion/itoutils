import json

from itoutils.django.nexus.api import NexusAPIClient


def test_client(mock_nexus_api):
    client = NexusAPIClient()
    dummy_send_payload = {"key": "value"}
    dummy_pks = ["a", "b"]
    dummy_pks_payload = [{"id": "a"}, {"id": "b"}]

    started_at = client.init_full_sync()
    [call] = mock_nexus_api.calls
    assert call.request.method == "POST"
    assert call.request.url == "http://nexus/api/sync-start"

    mock_nexus_api.reset()
    client.complete_full_sync(started_at)
    [call] = mock_nexus_api.calls
    assert call.request.method == "POST"
    assert call.request.url == "http://nexus/api/sync-completed"
    assert json.loads(call.request.content.decode()) == {"started_at": started_at}

    mock_nexus_api.reset()
    client.send_users(dummy_send_payload)
    [call] = mock_nexus_api.calls
    assert call.request.method == "POST"
    assert call.request.url == "http://nexus/api/users"
    assert json.loads(call.request.content.decode()) == dummy_send_payload

    mock_nexus_api.reset()
    client.delete_users(dummy_pks)
    [call] = mock_nexus_api.calls
    assert call.request.method == "DELETE"
    assert call.request.url == "http://nexus/api/users"
    assert json.loads(call.request.content.decode()) == dummy_pks_payload

    mock_nexus_api.reset()
    client.send_structures(dummy_send_payload)
    [call] = mock_nexus_api.calls
    assert call.request.method == "POST"
    assert call.request.url == "http://nexus/api/structures"
    assert json.loads(call.request.content.decode()) == dummy_send_payload

    mock_nexus_api.reset()
    client.delete_structures(dummy_pks)
    [call] = mock_nexus_api.calls
    assert call.request.method == "DELETE"
    assert call.request.url == "http://nexus/api/structures"
    assert json.loads(call.request.content.decode()) == dummy_pks_payload

    mock_nexus_api.reset()
    client.send_memberships(dummy_send_payload)
    [call] = mock_nexus_api.calls
    assert call.request.method == "POST"
    assert call.request.url == "http://nexus/api/memberships"
    assert json.loads(call.request.content.decode()) == dummy_send_payload

    mock_nexus_api.reset()
    client.delete_memberships(dummy_pks)
    [call] = mock_nexus_api.calls
    assert call.request.method == "DELETE"
    assert call.request.url == "http://nexus/api/memberships"
    assert json.loads(call.request.content.decode()) == dummy_pks_payload
