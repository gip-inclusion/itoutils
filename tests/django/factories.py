import functools

import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

DEFAULT_PASSWORD = "P4ssw0rd!*****"


@functools.cache
def default_password():
    return make_password(DEFAULT_PASSWORD)


class UserFactory(factory.django.DjangoModelFactory):
    """Generates User() objects for unit tests."""

    class Meta:
        model = User

    username = factory.Sequence("user_name{}".format)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Sequence("email{}@domain.com".format)
