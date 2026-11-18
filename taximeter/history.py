"""Ride history: append to data/rides.jsonl and query today's rides."""

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

DEFAULT_PATH = Path("data") / "rides.jsonl"


def save(duration_s: float, total_eur: Decimal, path: Path = DEFAULT_PATH) -> None:
    """Append one ride record to the JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "fecha": datetime.now(timezone.utc).isoformat(),
        "duracion_s": round(duration_s, 3),
        "total_eur": str(total_eur),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def rides_today(path: Path = DEFAULT_PATH) -> list[dict]:
    """Return all rides from today (local date)."""
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
    total = sum(Decimal(r["total_eur"]) for r in rides)
    return len(rides), total
