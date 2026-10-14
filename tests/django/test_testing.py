import inspect

import pytest
from django.contrib.auth.models import User
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from itoutils.django import testing
from itoutils.django.testing import assertSnapshotQueries
from testproject.testapp.models import Item


def test_assert_snapshot_queries(db, snapshot):
    with assertSnapshotQueries(snapshot):
        User.objects.count()


@pytest.fixture(name="items")
def items_fixture():
    parent = Item.objects.create(category="parent")
    Item.objects.create(category="child", parent=parent)


def test_assert_snapshot_queries_view_origin(db, items, client, snapshot):
    with assertSnapshotQueries(snapshot):
        response = client.get(reverse("item_list"))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_assert_snapshot_queries_transaction_origin(items, client, snapshot):
    with assertSnapshotQueries(snapshot):
        response = client.get(reverse("item_list"))
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("debug", [False, True])
def test_detect_origin_walks_the_same_frames_as_inspect_stack(items, client, monkeypatch, debug):
    """Equivalence test, checks that the frame walk returns exactly the same frames as inspect.stack().

    Context: _detect_origin walks the stack from sys._getframe(3), it used to call the slow inspect.stack()[3:].
    Spy on _walk_frames during real queries and check that, at the real call depth, it yields exactly the frames
    inspect.stack() would have, so that a wrong start frame (off by one) cannot silently change the origins.
    """
    if debug:
        # also exercise the code path taken when DEBUG_SQL_SNAPSHOT is set (needs template debug mode)
        monkeypatch.setenv("DEBUG_SQL_SNAPSHOT", "1")
    walk_frames = testing._walk_frames
    checked_calls = 0
    mismatches = []

    def checking_walk_frames(start_frame):
        nonlocal checked_calls
        checked_calls += 1
        # inspect.stack()[0] is this function and [1] is _detect_origin, which used to loop on inspect.stack()[3:]
        # this wrapper `checking_walk_frames` adds one frame, hence [4:] to get the same frames as the old loop
        expected = [(fi.frame, fi.filename, fi.lineno, fi.function) for fi in inspect.stack()[4:]]
        frame_infos = list(walk_frames(start_frame))
        # collect mismatches and assert at the end, rather than raising from inside the code under test
        if [tuple(frame_info) for frame_info in frame_infos] != expected:
            mismatches.append((frame_infos, expected))
        return frame_infos

    monkeypatch.setattr(testing, "_walk_frames", checking_walk_frames)
    with CaptureQueriesContext(connection) as context:
        response = client.get(reverse("item_list"))
    assert response.status_code == 200
    # every query went through the spy (and there was at least one), otherwise the test would pass vacuously
    assert checked_calls == len(context.captured_queries) > 0
    assert mismatches == []
