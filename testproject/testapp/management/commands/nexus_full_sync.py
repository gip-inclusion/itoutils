from itoutils.django.nexus.management.base_full_sync import BaseNexusFullSyncCommand
from testproject.testapp.models import Item


def serializer(item):
    return {"id": str(item.pk), "category": item.category}


class Command(BaseNexusFullSyncCommand):
    structure_serializer = staticmethod(serializer)
    user_serializer = staticmethod(serializer)
    membership_serializer = staticmethod(serializer)

    def get_users_queryset(self):
        return Item.objects.filter(category="user")

    def get_structures_queryset(self):
        return Item.objects.filter(category="structure")

    def get_memberships_queryset(self):
        return Item.objects.filter(category="membership")
