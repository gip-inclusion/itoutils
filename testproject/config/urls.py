from django.urls import include, path

from testproject.testapp import views

urlpatterns = [
    path("nexus/", include("itoutils.django.nexus.urls", namespace="nexus")),
    path("items/", views.item_list, name="item_list"),
]
