import sys

from django.conf import settings
from django.test import override_settings

from tests.utils.testing import reload_module

SOME_VALUE = settings.SECRET_KEY  # is mandatory


class TestReloadModule:
    def test_reload_module(self):
        current_module = sys.modules[__name__]
        assert current_module.SOME_VALUE == "django-insecure-%am#r-wl5tx8vp6+l7o+6)3+1iipnex@otx_%dtov7gbnud5t0"

        with override_settings(SECRET_KEY="supermario"):
            with reload_module(current_module):
                assert current_module.SOME_VALUE == "supermario"
            assert current_module.SOME_VALUE == "django-insecure-%am#r-wl5tx8vp6+l7o+6)3+1iipnex@otx_%dtov7gbnud5t0"
