import logging
from itertools import batched

from django.conf import settings
from django.core.management.base import BaseCommand

from itoutils.django.nexus.api import NexusAPIClient

logger = logging.getLogger(__name__)


class BaseNexusFullSyncCommand(BaseCommand):
    CHUNK_SIZE = 5_000
    structure_serializer = None
    user_serializer = None
    membership_serializer = None

    def batched(self, queryset):
        # NB : the iterator allows to fetch data in smaller batches.
        # Thanks to server-side cursors, any change occuring after the first
        # query won't affect the batches.
        return batched(queryset.iterator(), self.CHUNK_SIZE)

    def get_structures_queryset(self):
        raise NotImplementedError

    def serialize_structures(self, structures):
        return [self.structure_serializer(structure) for structure in structures]

    def sync_structures(self):
        for structures in self.batched(self.get_structures_queryset()):
            self.client.send_structures(self.serialize_structures(structures))

    def get_users_queryset(self):
        raise NotImplementedError

    def serialize_users(self, users):
        return [self.user_serializer(user) for user in users]

    def sync_users(self):
        for users in self.batched(self.get_users_queryset()):
            self.client.send_users(self.serialize_users(users))

    def get_memberships_queryset(self):
        raise NotImplementedError

    def serialize_memberships(self, memberships):
        return [self.membership_serializer(structure) for structure in memberships]

    def sync_memberships(self):
        for memberships in self.batched(self.get_memberships_queryset()):
            self.client.send_memberships(self.serialize_memberships(memberships))

    def handle(self, *args, no_checks=False, **kwargs):
        if not settings.NEXUS_API_BASE_URL:
            logger.warning("Nexus full sync is disabled")
        self.client = NexusAPIClient()
        start_at = self.client.init_full_sync()
        self.sync_structures()
        self.sync_users()
        self.sync_memberships()
        self.client.complete_full_sync(start_at)
