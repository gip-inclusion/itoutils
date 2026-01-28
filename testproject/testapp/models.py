from django.db import models

from itoutils.django.models import HasDataChangedMixin
from itoutils.django.nexus.models import NexusModelMixin, NexusQuerySetMixin


class Item(HasDataChangedMixin, models.Model):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", null=True)
    category = models.CharField()

    class Meta:
        app_label = "testapp"


def sync_items(items):
    pass


def delete_items(item_pks):
    pass


class SyncedItemQuerySet(NexusQuerySetMixin, models.QuerySet):
    nexus_tracked_fields = ["parent_id", "category", "sync_me"]
    nexus_sync = staticmethod(sync_items)
    nexus_delete = staticmethod(delete_items)

    def _get_nexus_queryset(self):
        return self.select_related("parent")


class SyncedItem(NexusModelMixin, models.Model):
    nexus_tracked_fields = ["parent_id", "category", "sync_me"]
    nexus_sync = staticmethod(sync_items)
    nexus_delete = staticmethod(delete_items)

    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", null=True)
    category = models.CharField()
    sync_me = models.BooleanField(default=True)

    def should_sync_to_nexus(self):
        # Don't sync if self.sync_me is False or self.parnet exists and has sync_me is False
        return self.sync_me and getattr(self.parent, "sync_me", True)

    objects = models.Manager.from_queryset(SyncedItemQuerySet)()
