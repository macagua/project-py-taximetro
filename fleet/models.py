"""Django models for the fleet app."""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Ride(models.Model):
    """A taxi ride — active while in progress, finished when complete."""

    STATUS_ACTIVE = "activa"
    STATUS_DONE = "finalizada"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Activa"),
        (STATUS_DONE, "Finalizada"),
    ]

    STATE_STOPPED = "parado"
    STATE_MOVING = "en_marcha"
    STATE_CHOICES = [
        (STATE_STOPPED, "Parado"),
        (STATE_MOVING, "En marcha"),
    ]

    driver = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rides",
        verbose_name="conductor",
    )
    fecha = models.DateTimeField(default=timezone.now, db_index=True)
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default=STATUS_DONE,
        db_index=True,
        verbose_name="estado",
    )
    vehicle_state = models.CharField(
        max_length=12,
        choices=STATE_CHOICES,
        default=STATE_STOPPED,
        verbose_name="estado vehículo",
    )
    # Null while the ride is in progress; set on finish
    duracion_s = models.FloatField(null=True, blank=True, verbose_name="duración (s)")
    total_eur = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        verbose_name="total (€)",
    )

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"

    def __str__(self) -> str:
        driver = self.driver.username if self.driver_id else "—"
        total = f"{self.total_eur} €" if self.total_eur is not None else "activa"
        return f"{self.fecha:%Y-%m-%d %H:%M}  {total}  ({driver})"
