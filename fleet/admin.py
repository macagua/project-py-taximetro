"""Django admin configuration for the fleet app."""

from django.contrib import admin
from django.contrib.auth.models import Group, User  # noqa: F401 — registered by auth

from fleet.models import Ride


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ("fecha", "driver", "duracion_s", "total_eur")
    list_filter = ("fecha", "driver")
    date_hierarchy = "fecha"
    search_fields = ("driver__username",)
    ordering = ("-fecha",)
    readonly_fields = ("fecha",)
