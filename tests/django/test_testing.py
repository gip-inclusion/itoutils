import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from itoutils.django.testing import assertSnapshotQueries
from testproject.testapp.models import Item


def test_assert_snapshot_queries(db, snapshot):
    with assertSnapshotQueries(snapshot):
        User.objects.count()


@pytest.fixture(name="items")
def items_fixture():
    parent = Item.objects.create(category="parent")
    Item.objects.create(category="child", parent=parent)


def test_assert_snapshot_queries_view_origin(db, items, client, snapshot):
    with assertSnapshotQueries(snapshot):
        response = client.get(reverse("item_list"))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_assert_snapshot_queries_transaction_origin(items, client, snapshot):
    with assertSnapshotQueries(snapshot):
        response = client.get(reverse("item_list"))
    assert response.status_code == 200
