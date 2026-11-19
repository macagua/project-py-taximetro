"""Tests for the REST API — uses ninja.testing.TestClient (no HTTP server needed)."""

import pytest
from django.contrib.auth import get_user_model
from ninja.testing import TestClient

from fleet.api import api
from fleet.models import Ride

User = get_user_model()

client = TestClient(api)


@pytest.fixture
def driver(db):
    return User.objects.create_user(username="taxista", password="segura1234")


# ---------------------------------------------------------------------------
# POST /rides
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_start_ride_creates_active_ride(driver):
    response = client.post("/rides", user=driver)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "activa"
    assert data["vehicle_state"] == "parado"
    assert Ride.objects.filter(pk=data["id"], status=Ride.STATUS_ACTIVE).exists()


# ---------------------------------------------------------------------------
# PATCH /rides/{id}/state
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_change_state_to_moving(driver):
    ride = Ride.objects.create(driver=driver, status=Ride.STATUS_ACTIVE)
    response = client.patch(
        f"/rides/{ride.pk}/state",
        json={"vehicle_state": "en_marcha"},
        user=driver,
    )
    assert response.status_code == 200
    assert response.json()["vehicle_state"] == "en_marcha"


@pytest.mark.django_db
def test_change_state_invalid_value_returns_400(driver):
    ride = Ride.objects.create(driver=driver, status=Ride.STATUS_ACTIVE)
    response = client.patch(
        f"/rides/{ride.pk}/state",
        json={"vehicle_state": "volando"},
        user=driver,
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_change_state_on_finished_ride_returns_404(driver):
    ride = Ride.objects.create(
        driver=driver, status=Ride.STATUS_DONE,
        duracion_s=60.0, total_eur="1.20",
    )
    response = client.patch(
        f"/rides/{ride.pk}/state",
        json={"vehicle_state": "en_marcha"},
        user=driver,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /rides/{id}/finish
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_finish_ride(driver):
    ride = Ride.objects.create(driver=driver, status=Ride.STATUS_ACTIVE)
    response = client.post(
        f"/rides/{ride.pk}/finish",
        json={"duracion_s": 120.5, "total_eur": "3.45"},
        user=driver,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "finalizada"
    assert float(data["duracion_s"]) == pytest.approx(120.5)
    assert data["total_eur"] == "3.45"
    ride.refresh_from_db()
    assert ride.status == Ride.STATUS_DONE


@pytest.mark.django_db
def test_finish_already_finished_returns_404(driver):
    ride = Ride.objects.create(
        driver=driver, status=Ride.STATUS_DONE,
        duracion_s=60.0, total_eur="1.20",
    )
    response = client.post(
        f"/rides/{ride.pk}/finish",
        json={"duracion_s": 60.0, "total_eur": "1.20"},
        user=driver,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /rides
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_list_rides_today(driver):
    Ride.objects.create(
        driver=driver, status=Ride.STATUS_DONE,
        duracion_s=60.0, total_eur="1.20",
    )
    response = client.get("/rides", user=driver)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.django_db
def test_list_rides_excludes_other_driver(driver):
    other = User.objects.create_user(username="otro", password="segura1234")
    Ride.objects.create(
        driver=other, status=Ride.STATUS_DONE,
        duracion_s=60.0, total_eur="1.20",
    )
    response = client.get("/rides", user=driver)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_list_rides_filter_by_date(driver):
    Ride.objects.create(
        driver=driver, status=Ride.STATUS_DONE,
        duracion_s=60.0, total_eur="1.20",
    )
    response = client.get("/rides?date=2000-01-01", user=driver)
    assert response.status_code == 200
    assert response.json() == []
