from django.db import models

from itoutils.django.models import HasDataChangedMixin


class Item(models.Model, HasDataChangedMixin):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", null=True)
    category = models.CharField()

    class Meta:
        app_label = "testapp"
