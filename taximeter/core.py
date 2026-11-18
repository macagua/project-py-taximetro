"""Business objects: Taximeter and Ride."""

import time
from decimal import Decimal, ROUND_HALF_UP
from typing import Callable

from taximeter.config import Tariffs, load as load_tariffs

# Default tariffs kept as module constants for tests that build Ride directly.
RATE_STOPPED: Decimal = Decimal("0.02")  # €/second when stopped or <20 km/h
RATE_MOVING:  Decimal = Decimal("0.05")  # €/second when moving

_DEFAULT_TARIFFS = Tariffs(RATE_STOPPED, RATE_MOVING)


class Ride:
    """Tracks the state and accumulated fare for a single trip.

    Args:
        now:     Callable returning a monotonic float. Defaults to time.monotonic.
        tariffs: Tariff rates to apply. Defaults to module-level defaults.

    Initial state is STOPPED (parado) — lower rate protects the passenger
    if the system starts while the taxi is waiting at a traffic light.
    """

    def __init__(
        self,
        now: Callable[[], float] = time.monotonic,
        tariffs: Tariffs = _DEFAULT_TARIFFS,
    ) -> None:
        self._now = now
        self._tariffs = tariffs
        self._state: str = "parado"       # "parado" | "en_marcha"
        self._fare: Decimal = Decimal("0")
        self._started_at: float = now()
        self._last_tick: float = self._started_at

    @property
    def state(self) -> str:
        return self._state

    @property
    def fare(self) -> Decimal:
        """Current accumulated fare rounded to 2 decimal places."""
        return self._fare.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        """Accumulate fare from _last_tick to now at the current rate."""
        now = self._now()
        elapsed = Decimal(str(now - self._last_tick))
        rate = self._tariffs.moving if self._state == "en_marcha" else self._tariffs.stopped
        self._fare += elapsed * rate
        self._last_tick = now

    def set_stopped(self) -> bool:
        """Switch to stopped state. Returns False if already stopped."""
        if self._state == "parado":
            return False
        self._tick()
        self._state = "parado"
        return True

    def set_moving(self) -> bool:
        """Switch to moving state. Returns False if already moving."""
        if self._state == "en_marcha":
            return False
        self._tick()
        self._state = "en_marcha"
        return True

    @property
    def duration_s(self) -> float:
        """Elapsed seconds since the ride started (up to the last tick)."""
        return self._last_tick - self._started_at

    def finish(self) -> Decimal:
        """Close the ride and return the total fare (ROUND_HALF_UP)."""
        self._tick()
        return self.fare


class Taximeter:
    """Orchestrates rides. Holds at most one active ride at a time.

    Args:
        now: Injectable clock forwarded to each Ride.
    """

    def __init__(self, now: Callable[[], float] = time.monotonic) -> None:
        self._now = now
        self._current_ride: Ride | None = None

    def start_ride(self) -> Ride:
        """Create and return a new Ride with tariffs loaded from config."""
        self._current_ride = Ride(now=self._now, tariffs=load_tariffs())
        return self._current_ride

    @property
    def current_ride(self) -> Ride | None:
        return self._current_ride
