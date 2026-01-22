import json

from django.core.management import call_command

from testproject.testapp.models import Item


def test_full_sync(db, mock_nexus_api):
    structure = Item.objects.create(category="structure")
    membership = Item.objects.create(category="membership")
    user = Item.objects.create(category="user")

    call_command("nexus_full_sync")

    [call_init, call_sync_structures, call_sync_users, call_sync_memberships, call_completed] = mock_nexus_api.calls

    assert call_init.request.method == "POST"
    assert call_init.request.url == "http://nexus/api/sync-start"
    started_at = call_init.response.json()["started_at"]

    assert call_sync_structures.request.method == "POST"
    assert call_sync_structures.request.url == "http://nexus/api/structures"
    assert json.loads(call_sync_structures.request.content.decode()) == [
        {"id": str(structure.pk), "category": "structure"}
    ]

    assert call_sync_users.request.method == "POST"
    assert call_sync_users.request.url == "http://nexus/api/users"
    assert json.loads(call_sync_users.request.content.decode()) == [{"id": str(user.pk), "category": "user"}]

    assert call_sync_memberships.request.method == "POST"
    assert call_sync_memberships.request.url == "http://nexus/api/memberships"
    assert json.loads(call_sync_memberships.request.content.decode()) == [
        {"id": str(membership.pk), "category": "membership"}
    ]

    assert call_completed.request.method == "POST"
    assert call_completed.request.url == "http://nexus/api/sync-completed"
    assert json.loads(call_completed.request.content.decode()) == {"started_at": started_at}
