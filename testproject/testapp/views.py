from django.shortcuts import render

from testproject.testapp.models import Item


def item_list(request):
    return render(request, "testapp/item_list.html", {"items": Item.objects.all()})
