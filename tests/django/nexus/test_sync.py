import unittest

import pytest

from testproject.testapp.models import SyncedItem
from tests.django.factories import SyncedItemFactory


class TestSync:
    @pytest.fixture(autouse=True)
    def setup_mocks(self, mocker):
        self.model_mocked_sync = mocker.patch("testproject.testapp.models.SyncedItem.nexus_sync")
        self.model_mocked_delete = mocker.patch("testproject.testapp.models.SyncedItem.nexus_delete")
        self.manager_mocked_sync = mocker.patch("testproject.testapp.models.SyncedItemQuerySet.nexus_sync")
        self.manager_mocked_delete = mocker.patch("testproject.testapp.models.SyncedItemQuerySet.nexus_delete")

    def reset_mocks(self):
        self.model_mocked_sync.reset_mock()
        self.model_mocked_delete.reset_mock()
        self.manager_mocked_sync.reset_mock()
        self.manager_mocked_delete.reset_mock()

    def test_sync_on_model_save(self, nexus_sync):
        synced_item = SyncedItemFactory()
        synced_item.save()

        assert self.model_mocked_sync.call_args_list == [unittest.mock.call([synced_item])]
        assert self.model_mocked_delete.call_args_list == []
        assert self.manager_mocked_sync.call_args_list == []
        assert self.manager_mocked_delete.call_args_list == []

        # Saving agani won't trigger an api call
        self.reset_mocks()
        synced_item.save()
        assert self.model_mocked_sync.call_args_list == []
        assert self.model_mocked_delete.call_args_list == []
        assert self.manager_mocked_sync.call_args_list == []
        assert self.manager_mocked_delete.call_args_list == []

        self.reset_mocks()
        synced_item.category = "other_category"
        synced_item.save()
        assert self.model_mocked_sync.call_args_list == [unittest.mock.call([synced_item])]
        assert self.model_mocked_delete.call_args_list == []
        assert self.manager_mocked_sync.call_args_list == []
        assert self.manager_mocked_delete.call_args_list == []

    def test_delete_on_model_save(self, nexus_sync, mock_nexus_api):
        synced_item = SyncedItemFactory(sync_me=False)

        assert self.model_mocked_sync.call_args_list == []
        assert self.model_mocked_delete.call_args_list == [unittest.mock.call([synced_item.pk])]
        assert self.manager_mocked_sync.call_args_list == []
        assert self.manager_mocked_delete.call_args_list == []

    def test_delete_on_model_delete(self, nexus_sync, mock_nexus_api):
        synced_item = SyncedItemFactory()
        synced_item_id = synced_item.pk
        self.reset_mocks()

        synced_item.delete()
        assert self.model_mocked_sync.call_args_list == []
        assert self.model_mocked_delete.call_args_list == [unittest.mock.call([synced_item_id])]
        assert self.manager_mocked_sync.call_args_list == []
        assert self.manager_mocked_delete.call_args_list == []

    def test_sync_on_manager_update(self, nexus_sync, mock_nexus_api):
        synced_item_1 = SyncedItemFactory()
        synced_item_2 = SyncedItemFactory()
        self.reset_mocks()

        SyncedItem.objects.order_by("pk").update(category="blob")
        assert self.model_mocked_sync.call_args_list == []
        assert self.model_mocked_delete.call_args_list == []
        assert self.manager_mocked_sync.call_args_list == [unittest.mock.call([synced_item_1, synced_item_2])]
        assert self.manager_mocked_delete.call_args_list == []

    def test_delete_on_manager_update(self, nexus_sync, mock_nexus_api):
        synced_item_1 = SyncedItemFactory()
        synced_item_2 = SyncedItemFactory()
        self.reset_mocks()

        SyncedItem.objects.filter(pk=synced_item_1.pk).update(sync_me=False)
        assert self.model_mocked_sync.call_args_list == []
        assert self.model_mocked_delete.call_args_list == []
        assert self.manager_mocked_sync.call_args_list == []
        assert self.manager_mocked_delete.call_args_list == [unittest.mock.call([synced_item_1.pk])]

        synced_item_1.refresh_from_db()
        self.reset_mocks()
        SyncedItem.objects.filter(pk=synced_item_2.pk).update(parent=synced_item_1)
        assert self.model_mocked_sync.call_args_list == []
        assert self.model_mocked_delete.call_args_list == []
        assert self.manager_mocked_sync.call_args_list == []
        assert self.manager_mocked_delete.call_args_list == [unittest.mock.call([synced_item_2.pk])]

    def test_delete_on_manager_delete(self, nexus_sync, mock_nexus_api):
        synced_item_1 = SyncedItemFactory()
        synced_item_2 = SyncedItemFactory()
        self.reset_mocks()

        SyncedItem.objects.order_by("pk").delete()
        assert self.model_mocked_sync.call_args_list == []
        assert self.model_mocked_delete.call_args_list == []
        assert self.manager_mocked_sync.call_args_list == []
        assert self.manager_mocked_delete.call_args_list == [unittest.mock.call([synced_item_1.pk, synced_item_2.pk])]

    def test_sync_on_manager_bulk_update(self, nexus_sync, mock_nexus_api):
        synced_item_1 = SyncedItemFactory()
        synced_item_2 = SyncedItemFactory()
        self.reset_mocks()

        SyncedItem.objects.bulk_update([synced_item_1, synced_item_2], ["category"])
        assert self.model_mocked_sync.call_args_list == []
        assert self.model_mocked_delete.call_args_list == []
        assert self.manager_mocked_sync.call_args_list == [unittest.mock.call([synced_item_1, synced_item_2])]
        assert self.manager_mocked_delete.call_args_list == []

    def test_delete_on_manager_bulk_update(self, nexus_sync, mock_nexus_api):
        synced_item_1 = SyncedItemFactory()
        synced_item_2 = SyncedItemFactory()
        self.reset_mocks()

        synced_item_1.sync_me = False
        synced_item_2.sync_me = False

        SyncedItem.objects.bulk_update([synced_item_1, synced_item_2], ["sync_me"])
        assert self.model_mocked_sync.call_args_list == []
        assert self.model_mocked_delete.call_args_list == []
        assert self.manager_mocked_sync.call_args_list == []
        assert self.manager_mocked_delete.call_args_list == [unittest.mock.call([synced_item_1.pk, synced_item_2.pk])]

    def test_bulk_create(self, nexus_sync, mock_nexus_api):
        synced_item_1 = SyncedItemFactory.build()
        synced_item_2 = SyncedItemFactory.build()
        self.reset_mocks()

        with pytest.raises(NotImplementedError):
            SyncedItem.objects.bulk_create([synced_item_1, synced_item_2])
        assert SyncedItem.objects.count() == 0

        SyncedItem.objects.bulk_create([synced_item_1, synced_item_2], nexus_no_sync=True)
        assert SyncedItem.objects.count() == 2
        assert self.model_mocked_sync.call_args_list == []
        assert self.model_mocked_delete.call_args_list == []
        assert self.manager_mocked_sync.call_args_list == []
        assert self.manager_mocked_delete.call_args_list == []
