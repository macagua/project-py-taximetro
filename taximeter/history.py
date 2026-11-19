"""Ride history.

Primary backend: Django ORM (fleet.Ride) when Django is configured.
Fallback: JSONL file — used by tests that run without a Django setup.
"""

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

DEFAULT_PATH = Path("data") / "rides.jsonl"


def _django_ready() -> bool:
    try:
        from django.conf import settings

        return bool(getattr(settings, "DATABASES", None))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Public API  (same signatures as before)
# ---------------------------------------------------------------------------


def save(
    duration_s: float,
    total_eur: Decimal,
    path: Path = DEFAULT_PATH,
    driver=None,
) -> None:
    """Persist one completed ride (sync). Uses ORM when Django is ready."""
    if _django_ready():
        from fleet.models import Ride

        Ride.objects.create(duracion_s=duration_s, total_eur=total_eur, driver=driver)
        return

    # jsonl fallback
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "fecha": datetime.now(timezone.utc).isoformat(),
        "duracion_s": round(duration_s, 3),
        "total_eur": str(total_eur),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


async def asave(
    duration_s: float,
    total_eur: Decimal,
    driver=None,
) -> None:
    """Persist one completed ride (async). Required from async event handlers."""
    if _django_ready():
        from fleet.models import Ride

        await Ride.objects.acreate(
            duracion_s=duration_s, total_eur=total_eur, driver=driver
        )
        return

    # jsonl fallback via sync path wrapped in a thread
    from asgiref.sync import sync_to_async

    await sync_to_async(save)(duration_s, total_eur, driver=driver)


def rides_today(path: Path = DEFAULT_PATH) -> list[dict]:
    """Return today's rides as a list of dicts (ORM or jsonl)."""
    if _django_ready():
        from django.utils import timezone as tz
        from fleet.models import Ride

        today = tz.localdate()
        return [
            {
                "fecha": r.fecha.isoformat(),
                "duracion_s": r.duracion_s,
                "total_eur": str(r.total_eur),
            }
            for r in Ride.objects.filter(fecha__date=today)
        ]

    # jsonl fallback
    if not path.exists():
        return []
    today = datetime.now().date()
    rides = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            ride_date = datetime.fromisoformat(record["fecha"]).astimezone().date()
            if ride_date == today:
                rides.append(record)
    return rides


def summary_today(path: Path = DEFAULT_PATH) -> tuple[int, Decimal]:
    """Return (count, total_eur) for today's rides."""
    rides = rides_today(path)
    if _django_ready():
        total = sum(Decimal(r["total_eur"]) for r in rides)
    else:
        total = sum(Decimal(r["total_eur"]) for r in rides)
    return len(rides), total
