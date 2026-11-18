"""Tests for taximeter.history."""

from decimal import Decimal
from pathlib import Path
from taximeter import history


def test_save_creates_file(tmp_path):
    p = tmp_path / "rides.jsonl"
    history.save(10.0, Decimal("0.20"), path=p)
    assert p.exists()


def test_save_appends_records(tmp_path):
    p = tmp_path / "rides.jsonl"
    history.save(10.0, Decimal("0.20"), path=p)
    history.save(20.0, Decimal("1.00"), path=p)
    lines = p.read_text().strip().splitlines()
    assert len(lines) == 2


def test_save_record_fields(tmp_path):
    import json
    p = tmp_path / "rides.jsonl"
    history.save(5.5, Decimal("0.11"), path=p)
    record = json.loads(p.read_text())
    assert record["duracion_s"] == 5.5
    assert record["total_eur"] == "0.11"
    assert "fecha" in record


def test_rides_today_returns_todays_records(tmp_path):
    p = tmp_path / "rides.jsonl"
    history.save(10.0, Decimal("0.20"), path=p)
    history.save(20.0, Decimal("1.00"), path=p)
    rides = history.rides_today(path=p)
    assert len(rides) == 2


def test_rides_today_empty_when_no_file(tmp_path):
    p = tmp_path / "rides.jsonl"
    assert history.rides_today(path=p) == []


def test_summary_today(tmp_path):
    p = tmp_path / "rides.jsonl"
    history.save(10.0, Decimal("0.20"), path=p)
    history.save(20.0, Decimal("1.00"), path=p)
    count, total = history.summary_today(path=p)
    assert count == 2
    assert total == Decimal("1.20")


def test_summary_today_empty(tmp_path):
    p = tmp_path / "rides.jsonl"
    count, total = history.summary_today(path=p)
    assert count == 0
    assert total == Decimal("0")
