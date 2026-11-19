"""Django admin configuration for the fleet app."""

from django.contrib import admin
from django.contrib.auth.models import User, Group

# User and Group are already registered by django.contrib.auth.
# No custom models in this app yet — admin shows the built-in auth models.
