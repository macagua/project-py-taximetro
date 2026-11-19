"""REST API for the taximeter — exposed at /api/ via django-ninja."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

from fleet.models import Ride
import taximeter

api = NinjaAPI(
    title="TaxiTech API",
    description=f"API REST del {taximeter.__doc__[21:38]}.",
    auth=django_auth,
    urls_namespace="taxi_api",
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class RideOut(Schema):
    id: int
    fecha: datetime
    status: str
    vehicle_state: str
    duracion_s: Optional[float] = None
    total_eur: Optional[Decimal] = None


class StateIn(Schema):
    vehicle_state: str  # "parado" | "en_marcha"


class FinishIn(Schema):
    duracion_s: float
    total_eur: Decimal


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@api.post("/rides", response=RideOut, summary="Iniciar carrera")
def start_ride(request):
    """Crea una carrera activa asignada al usuario autenticado."""
    ride = Ride.objects.create(
        driver=request.user,
        status=Ride.STATUS_ACTIVE,
        vehicle_state=Ride.STATE_STOPPED,
    )
    return ride


@api.patch("/rides/{ride_id}/state", response=RideOut, summary="Cambiar estado vehículo")
def change_state(request, ride_id: int, payload: StateIn):
    """Cambia el estado del vehículo (parado / en_marcha) de una carrera activa."""
    if payload.vehicle_state not in (Ride.STATE_STOPPED, Ride.STATE_MOVING):
        return api.create_response(
            request, {"detail": "Estado inválido. Use 'parado' o 'en_marcha'."}, status=400
        )
    ride = get_object_or_404(Ride, pk=ride_id, driver=request.user, status=Ride.STATUS_ACTIVE)
    ride.vehicle_state = payload.vehicle_state
    ride.save(update_fields=["vehicle_state"])
    return ride


@api.post("/rides/{ride_id}/finish", response=RideOut, summary="Finalizar carrera")
def finish_ride(request, ride_id: int, payload: FinishIn):
    """Cierra una carrera activa y registra duración y total."""
    ride = get_object_or_404(Ride, pk=ride_id, driver=request.user, status=Ride.STATUS_ACTIVE)
    ride.status = Ride.STATUS_DONE
    ride.duracion_s = payload.duracion_s
    ride.total_eur = payload.total_eur
    ride.save(update_fields=["status", "duracion_s", "total_eur"])
    return ride


@api.get("/rides", response=list[RideOut], summary="Listar carreras por fecha")
def list_rides(request, date: Optional[date] = None):
    """Devuelve las carreras finalizadas de una fecha (por defecto hoy)."""
    from django.utils import timezone as tz
    target = date or tz.localdate()
    return Ride.objects.filter(
        driver=request.user,
        status=Ride.STATUS_DONE,
        fecha__date=target,
    )
