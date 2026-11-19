"""Tests for taximeter.config — tariff loading and fallback."""

import logging
from decimal import Decimal
from pathlib import Path
from taximeter.config import load, DEFAULT_STOPPED, DEFAULT_MOVING


def write_toml(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_load_valid_config(tmp_path):
    p = write_toml(
        tmp_path / "tariffs.toml", "[tariffs]\nstopped = 0.03\nmoving = 0.06\n"
    )
    t = load(path=p)
    assert t.stopped == Decimal("0.03")
    assert t.moving == Decimal("0.06")


def test_load_missing_file_uses_defaults(tmp_path):
    t = load(path=tmp_path / "nonexistent.toml")
    assert t.stopped == DEFAULT_STOPPED
    assert t.moving == DEFAULT_MOVING


def test_load_missing_key_uses_defaults(tmp_path):
    # 'moving' key absent
    p = write_toml(tmp_path / "tariffs.toml", "[tariffs]\nstopped = 0.02\n")
    t = load(path=p)
    assert t.stopped == DEFAULT_STOPPED
    assert t.moving == DEFAULT_MOVING


def test_load_negative_value_uses_defaults(tmp_path):
    p = write_toml(
        tmp_path / "tariffs.toml", "[tariffs]\nstopped = -0.02\nmoving = 0.05\n"
    )
    t = load(path=p)
    assert t.stopped == DEFAULT_STOPPED
    assert t.moving == DEFAULT_MOVING


def test_load_non_numeric_value_uses_defaults(tmp_path):
    p = write_toml(
        tmp_path / "tariffs.toml", '[tariffs]\nstopped = "fast"\nmoving = 0.05\n'
    )
    t = load(path=p)
    assert t.stopped == DEFAULT_STOPPED
    assert t.moving == DEFAULT_MOVING


def test_load_invalid_emits_warning(tmp_path, caplog):
    p = write_toml(
        tmp_path / "tariffs.toml", "[tariffs]\nstopped = -1\nmoving = 0.05\n"
    )
    with caplog.at_level(logging.WARNING, logger="taximeter"):
        load(path=p)
    assert any("por defecto" in r.message for r in caplog.records)
