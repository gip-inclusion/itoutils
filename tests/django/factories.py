import factory
from django.contrib.auth.models import User

from testproject.testapp.models import SyncedItem


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence("user_name{}".format)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence("email{}@domain.com".format)


class SyncedItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SyncedItem

    user = factory.SubFactory(UserFactory)
    category = factory.Faker("word")
