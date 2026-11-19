"""Tests for taximeter.history — uses Django ORM backend (pytest-django)."""

import pytest
from decimal import Decimal
from taximeter import history


@pytest.mark.django_db
def test_save_creates_ride(tmp_path):
    history.save(10.0, Decimal("0.20"))
    from fleet.models import Ride
    assert Ride.objects.filter(duracion_s=10.0, total_eur=Decimal("0.20")).exists()


@pytest.mark.django_db
def test_save_appends_records(tmp_path):
    history.save(10.0, Decimal("0.20"))
    history.save(20.0, Decimal("1.00"))
    from fleet.models import Ride
    assert Ride.objects.count() == 2


@pytest.mark.django_db
def test_save_record_fields(tmp_path):
    history.save(5.5, Decimal("0.11"))
    from fleet.models import Ride
    ride = Ride.objects.get()
    assert ride.duracion_s == 5.5
    assert ride.total_eur == Decimal("0.11")
    assert ride.fecha is not None


@pytest.mark.django_db
def test_rides_today_returns_todays_records():
    history.save(10.0, Decimal("0.20"))
    history.save(20.0, Decimal("1.00"))
    rides = history.rides_today()
    assert len(rides) == 2


@pytest.mark.django_db
def test_rides_today_empty_when_no_records():
    assert history.rides_today() == []


@pytest.mark.django_db
def test_summary_today():
    history.save(10.0, Decimal("0.20"))
    history.save(20.0, Decimal("1.00"))
    count, total = history.summary_today()
    assert count == 2
    assert total == Decimal("1.20")


@pytest.mark.django_db
def test_summary_today_empty():
    count, total = history.summary_today()
    assert count == 0
    assert total == Decimal("0")
