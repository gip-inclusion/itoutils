import datetime

import pytest
from django.contrib.auth.models import User
from freezegun import freeze_time
from jwcrypto import jwt

from itoutils.nexus.utils import EXPIRY_DELAY, decode_jwt, generate_jwt


def test_generate_and_decode_jwt(db):
    with freeze_time() as frozen_now:
        user = User.objects.create(email="moi@mailinator.com")
        token = generate_jwt(user)

        # generated token requires a key to decode
        with pytest.raises(KeyError):
            jwt.JWT(jwt=token).claims  # noqa: B018

        # It contains the user email
        assert decode_jwt(token) == {"email": "moi@mailinator.com"}

        # Wait for the JWT to expire, and then extra time for the leeway.
        leeway = 60
        frozen_now.tick(datetime.timedelta(seconds=EXPIRY_DELAY + leeway + 1))
        with pytest.raises(ValueError):
            decode_jwt(token)
