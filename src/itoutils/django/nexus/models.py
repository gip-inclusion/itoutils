from django.db import transaction
from django.db.models import ForeignKey
from django.db.models.functions import Cast

from itoutils.django.models import HasDataChangedMixin


class NexusQuerySetMixin:
    nexus_tracked_fields = None
    nexus_sync = None
    nexus_delete = None

    def _sync_or_delete(self, objs):
        to_sync = []
        to_delete = []
        for obj in objs:
            if obj.should_sync_to_nexus():
                to_sync.append(obj)
            else:
                to_delete.append(obj)
        if to_sync:
            # maybe replace lambda with partial(self.nexus_sync, to_sync) ?
            transaction.on_commit(lambda: self.nexus_sync(to_sync))
        if to_delete:
            transaction.on_commit(lambda: self.nexus_delete([obj.pk for obj in to_delete]))

    def _get_nexus_queryset(self):
        # Allow to select_related users and siaes for memberships
        return self

    def get_updated_fields(self, fields):
        # Allow to detect foreign keys update
        return {
            f"{field}_id" if isinstance(self.model._meta.get_field(field), ForeignKey) else field for field in fields
        }

    def update(self, **kwargs):
        sync = True
        for value in kwargs.values():
            if isinstance(value, Cast):
                sync = False
                break
        if sync and self.get_updated_fields(kwargs.keys()) & set(self.nexus_tracked_fields):
            objs = self._get_nexus_queryset()
            for field, value in kwargs.items():
                for obj in objs:
                    setattr(obj, field, value)
            self._sync_or_delete(objs)
        return super().update(**kwargs)

    def delete(self):
        transaction.on_commit(lambda: self.nexus_delete([obj.pk for obj in self]))
        return super().delete()

    def bulk_create(self, objs, *args, nexus_no_sync=False, **kwargs):
        if nexus_no_sync:
            # We don't want to handle this method if conflicts are ignored or updated
            # Only allow to call this if the caller knows he needs to sync the objects himself
            return super().bulk_create(objs, *args, **kwargs)
        raise NotImplementedError

    def bulk_update(self, objs, fields, batch_size=None):
        if self.get_updated_fields(fields) & set(self.nexus_tracked_fields):
            # Beware of 1+N requests with user memberships
            self._sync_or_delete(objs)
        # bulk_update calls update with Cast expressins as values
        # We skip sync in update when we see such values
        return super().bulk_update(objs, fields, batch_size)


class NexusModelMixin(HasDataChangedMixin):
    nexus_tracked_fields = None
    nexus_sync = None
    nexus_delete = None

    def should_sync_to_nexus(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        should_sync = should_delete = False
        if self.has_data_changed(self.nexus_tracked_fields):
            if self.should_sync_to_nexus():
                should_sync = True
            else:
                should_delete = True

        super().save(*args, **kwargs)

        if should_sync:
            transaction.on_commit(lambda: self.nexus_sync([self]))
        if should_delete:
            transaction.on_commit(lambda: self.nexus_delete([self.pk]))

    def delete(self, *args, **kwargs):
        transaction.on_commit(lambda: self.nexus_delete([self.pk]))
        return super().delete(*args, **kwargs)
