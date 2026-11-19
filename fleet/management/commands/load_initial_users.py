"""Management command: crea los usuarios iniciales si no existen."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

INITIAL_USERS = [
    {"username": "admin",    "password": "admin",        "email": "admin@test.com", "is_superuser": True,  "is_staff": True},
    {"username": "anapoleo", "password": "c@rolina123",  "email": "anapoleo@gmail.com", "is_superuser": False, "is_staff": True},
    {"username": "leonardo", "password": "caballero123", "email": "leonardocaballero@gmail.com", "is_superuser": False, "is_staff": True},
]


class Command(BaseCommand):
    help = "Crea los usuarios iniciales del sistema (idempotente)."

    def handle(self, *args, **options):
        User = get_user_model()
        for data in INITIAL_USERS:
            user, created = User.objects.get_or_create(username=data["username"])
            if created:
                user.set_password(data["password"])
                user.set_password(data["email"])
                user.is_superuser = data["is_superuser"]
                user.is_staff = data["is_staff"]
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  ✓ Usuario creado: {data['username']}"))
            else:
                self.stdout.write(f"  · Ya existe: {data['username']}")
