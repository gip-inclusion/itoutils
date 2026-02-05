import itertools
from functools import partial

from django.db import transaction

from itoutils.django.models import HasDataChangedMixin


class NexusQuerySetMixin:
    def _sync_or_delete(self, objs):
        to_sync = []
        to_delete = []
        for obj in objs:
            if obj.should_sync_to_nexus():
                to_sync.append(obj)
            else:
                to_delete.append(obj)
        if to_sync:
            transaction.on_commit(partial(self.model.nexus_sync, to_sync))
        if to_delete:
            transaction.on_commit(partial(self.model.nexus_delete, [obj.pk for obj in to_delete]))

    def _get_nexus_queryset(self):
        # In case should_sync_to_nexus crosses relationships, add a select_related models here
        return self.model.objects

    def get_updated_fields(self, fields):
        updated_fields = set(fields)
        for fieldname in fields:
            field = self.model._meta.get_field(fieldname)
            if field.is_relation and field.concrete:
                updated_fields.add(field.attname)
        return updated_fields

    def update(self, **kwargs):
        pks_to_sync = []
        if self.get_updated_fields(kwargs.keys()) & set(self.model.nexus_tracked_fields):
            pks_to_sync = list(self.values_list("pk", flat=True))
        result = super().update(**kwargs)
        if pks_to_sync:
            for batch in itertools.batched(self._get_nexus_queryset().filter(pk__in=pks_to_sync), 10_000):
                self._sync_or_delete(batch)
        return result

    def delete(self):
        transaction.on_commit(partial(self.model.nexus_delete, list(self.values_list("pk", flat=True))))
        return super().delete()

    # bulk_update calls update so it's correctly handled (see the tests)

    def bulk_create(self, objs, *args, skip_nexus_sync=False, **kwargs):
        if skip_nexus_sync:
            # We don't want to handle this method if conflicts are ignored or updated
            # Only allow to call this if the caller knows he needs to sync the objects himself
            return super().bulk_create(objs, *args, **kwargs)
        raise NotImplementedError


class NexusModelMixin(HasDataChangedMixin):
    nexus_tracked_fields = None
    nexus_sync = None
    nexus_delete = None

    def should_sync_to_nexus(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        sync_needed = self.has_data_changed(self.nexus_tracked_fields)

        super().save(*args, **kwargs)

        if sync_needed:
            if self.should_sync_to_nexus():
                transaction.on_commit(partial(self.nexus_sync, [self]))
            else:
                transaction.on_commit(partial(self.nexus_delete, [self.pk]))

    def delete(self, *args, **kwargs):
        transaction.on_commit(partial(self.nexus_delete, [self.pk]))
        return super().delete(*args, **kwargs)
