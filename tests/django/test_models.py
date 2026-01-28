import pytest

from testproject.testapp.models import Item


@pytest.mark.django_db
def test_has_data_changed_mixin():
    item = Item.objects.create(category="a")
    # New object
    new_item = Item(category="b", parent=item)
    assert new_item.has_data_changed(["category"])
    assert new_item.has_data_changed(["parent_id"])

    new_item.save()
    assert not new_item.has_data_changed(["category"])
    assert not new_item.has_data_changed(["parent_id"])

    new_item.category = "c"
    new_item.parent = new_item
    assert new_item.has_data_changed(["category"])
    assert new_item.has_data_changed(["parent_id"])
