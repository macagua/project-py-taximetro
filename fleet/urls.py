from django.contrib import admin
from django.conf.urls import include
from django.urls import path

from fleet.api import api

urlpatterns = [
    path("grappelli/", include("grappelli.urls")),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
