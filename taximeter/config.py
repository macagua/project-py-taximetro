"""Tariff configuration loaded from config/tariffs.toml."""

import logging
import tomllib
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

CONFIG_PATH = Path("config") / "tariffs.toml"

DEFAULT_STOPPED = Decimal("0.02")
DEFAULT_MOVING  = Decimal("0.05")

log = logging.getLogger("taximeter")


@dataclass(frozen=True)
class Tariffs:
    stopped: Decimal
    moving: Decimal


def load(path: Path = CONFIG_PATH) -> Tariffs:
    """Read tariffs from TOML. Falls back to defaults on any error."""
    if not path.exists():
        log.warning("Archivo de tarifas no encontrado (%s). Usando valores por defecto.", path)
        return Tariffs(DEFAULT_STOPPED, DEFAULT_MOVING)

    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
        stopped = Decimal(str(data["tariffs"]["stopped"]))
        moving  = Decimal(str(data["tariffs"]["moving"]))
        if stopped <= 0 or moving <= 0:
            raise ValueError("Las tarifas deben ser positivas")
        return Tariffs(stopped, moving)
    except Exception as exc:
        log.warning("Config inválida (%s). Usando valores por defecto. Causa: %s", path, exc)
        return Tariffs(DEFAULT_STOPPED, DEFAULT_MOVING)
