import pytest

from testproject.testapp.models import SyncedItem
from tests.django.factories import SyncedItemFactory, UserFactory


class TestSync:
    @pytest.fixture(autouse=True)
    def setup_mocks(self, mocker):
        self.mocked_sync = mocker.patch("testproject.testapp.models.SyncedItem.nexus_sync")
        self.mocked_delete = mocker.patch("testproject.testapp.models.SyncedItem.nexus_delete")

    def assert_mocked_calls(self, sync=False, delete=False, args=None):
        if sync:
            assert self.mocked_sync.call_count == 1
            assert set(self.mocked_sync.call_args_list[0][0][0]) == set(args)
        else:
            assert self.mocked_sync.call_count == 0
        if delete:
            assert self.mocked_delete.call_count == 1
            assert set(self.mocked_delete.call_args_list[0][0][0]) == set(args)
        else:
            assert self.mocked_delete.call_count == 0

    def test_sync_on_model_save_new_instance(self, db, django_capture_on_commit_callbacks):
        with django_capture_on_commit_callbacks(execute=True):
            synced_item = SyncedItemFactory()
        self.assert_mocked_calls(sync=True, args=[synced_item])

    def test_sync_on_model_save_tracked_field(self, db, django_capture_on_commit_callbacks):
        synced_item = SyncedItemFactory()

        with django_capture_on_commit_callbacks(execute=True):
            synced_item.user = UserFactory()
            synced_item.save()
        self.assert_mocked_calls(sync=True, args=[synced_item])

    def test_no_sync_on_model_save_no_changed_data(self, db, django_capture_on_commit_callbacks):
        synced_item = SyncedItemFactory()

        with django_capture_on_commit_callbacks(execute=True):
            synced_item.save()
        self.assert_mocked_calls(None)

    def test_no_sync_on_model_save_non_tracked_field(self, db, django_capture_on_commit_callbacks):
        synced_item = SyncedItemFactory()

        with django_capture_on_commit_callbacks(execute=True):
            synced_item.category = "other_category"
            synced_item.save()
        self.assert_mocked_calls(None)

    def test_delete_on_model_save(self, db, django_capture_on_commit_callbacks, mock_nexus_api):
        with django_capture_on_commit_callbacks(execute=True):
            synced_item = SyncedItemFactory(sync_me=False)
        self.assert_mocked_calls(delete=True, args=[synced_item.pk])

    def test_delete_on_model_delete(self, db, django_capture_on_commit_callbacks, mock_nexus_api):
        synced_item = SyncedItemFactory()
        synced_item_id = synced_item.pk

        with django_capture_on_commit_callbacks(execute=True):
            synced_item.delete()
        self.assert_mocked_calls(delete=True, args=[synced_item_id])

    def test_sync_on_manager_update(self, db, django_capture_on_commit_callbacks, mock_nexus_api):
        synced_item_1 = SyncedItemFactory()
        synced_item_2 = SyncedItemFactory()

        with django_capture_on_commit_callbacks(execute=True):
            SyncedItem.objects.order_by("pk").update(sync_me=True, user=UserFactory())
        self.assert_mocked_calls(sync=True, args=[synced_item_1, synced_item_2])

    def test_sync_on_manager_update_filtered_value_changed(
        self, db, django_capture_on_commit_callbacks, mock_nexus_api
    ):
        synced_item_1 = SyncedItemFactory(category="a")
        synced_item_2 = SyncedItemFactory(category="a")

        with django_capture_on_commit_callbacks(execute=True):
            SyncedItem.objects.order_by("pk").update(sync_me=True, category="b")
        self.assert_mocked_calls(sync=True, args=[synced_item_1, synced_item_2])

    def test_delete_on_manager_update(self, db, django_capture_on_commit_callbacks, mock_nexus_api):
        synced_item = SyncedItemFactory()

        with django_capture_on_commit_callbacks(execute=True):
            SyncedItem.objects.update(sync_me=False)
        self.assert_mocked_calls(delete=True, args=[synced_item.pk])

    def test_delete_on_manager_update_related_object(self, db, django_capture_on_commit_callbacks, mock_nexus_api):
        synced_item = SyncedItemFactory(user__is_active=False)

        with django_capture_on_commit_callbacks(execute=True):
            SyncedItem.objects.update(sync_me=True)
        self.assert_mocked_calls(delete=True, args=[synced_item.pk])

    def test_delete_on_manager_delete(self, db, django_capture_on_commit_callbacks, mock_nexus_api):
        synced_item_1 = SyncedItemFactory()
        synced_item_2 = SyncedItemFactory()

        with django_capture_on_commit_callbacks(execute=True):
            SyncedItem.objects.order_by("pk").delete()
        self.assert_mocked_calls(delete=True, args=[synced_item_1.pk, synced_item_2.pk])

    def test_sync_on_manager_bulk_update(self, db, django_capture_on_commit_callbacks, mock_nexus_api):
        synced_item_1 = SyncedItemFactory()
        synced_item_2 = SyncedItemFactory()

        with django_capture_on_commit_callbacks(execute=True):
            SyncedItem.objects.bulk_update([synced_item_1, synced_item_2], ["sync_me"])
        self.assert_mocked_calls(sync=True, args=[synced_item_1, synced_item_2])

    def test_delete_on_manager_bulk_update(self, db, django_capture_on_commit_callbacks, mock_nexus_api):
        synced_item_1 = SyncedItemFactory()
        synced_item_2 = SyncedItemFactory()

        with django_capture_on_commit_callbacks(execute=True):
            synced_item_1.sync_me = False
            synced_item_2.sync_me = False
            SyncedItem.objects.bulk_update([synced_item_1, synced_item_2], ["sync_me"])
        self.assert_mocked_calls(delete=True, args=[synced_item_1.pk, synced_item_2.pk])

    def test_bulk_create(self, db, django_capture_on_commit_callbacks, mock_nexus_api):
        user = UserFactory()
        synced_item_1 = SyncedItemFactory.build(user=user)
        synced_item_2 = SyncedItemFactory.build(user=user)

        with pytest.raises(NotImplementedError):
            SyncedItem.objects.bulk_create([synced_item_1, synced_item_2], ignore_conflicts=True)
        assert SyncedItem.objects.count() == 0

        with pytest.raises(NotImplementedError):
            SyncedItem.objects.bulk_create([synced_item_1, synced_item_2], update_conflicts=True)
        assert SyncedItem.objects.count() == 0

        with django_capture_on_commit_callbacks(execute=True):
            SyncedItem.objects.bulk_create([synced_item_1, synced_item_2])
        self.assert_mocked_calls(sync=True, args=[synced_item_1, synced_item_2])
