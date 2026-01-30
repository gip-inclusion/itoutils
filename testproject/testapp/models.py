from django.contrib.auth.models import User
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
    def _get_nexus_queryset(self):
        return super()._get_nexus_queryset().select_related("user")


class SyncedItem(NexusModelMixin, models.Model):
    nexus_tracked_fields = ["user_id", "sync_me"]
    nexus_sync = staticmethod(sync_items)
    nexus_delete = staticmethod(delete_items)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField()
    sync_me = models.BooleanField(default=True)

    def should_sync_to_nexus(self):
        return self.sync_me and self.user.is_active

    objects = models.Manager.from_queryset(SyncedItemQuerySet)()
