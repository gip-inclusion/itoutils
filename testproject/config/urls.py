from django.urls import include, path

urlpatterns = [
    path("nexus/", include("itoutils.nexus.urls", namespace="nexus")),
]
