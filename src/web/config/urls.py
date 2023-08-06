from django.urls import include
from django.urls import path

urlpatterns = [
    path("api/", include("web.accounts.urls")),
]
