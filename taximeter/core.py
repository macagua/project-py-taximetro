"""Business objects: Taximeter and Ride."""

import time
from decimal import Decimal, ROUND_HALF_UP
from typing import Callable

# Tariffs (Zona EMT Madrid, June 2025)
RATE_STOPPED: Decimal = Decimal("0.02")  # €/second when stopped or <20 km/h
RATE_MOVING:  Decimal = Decimal("0.05")  # €/second when moving


class Ride:
    """Tracks the state and accumulated fare for a single trip.

    Args:
        now: Callable that returns a monotonic float (seconds).
             Defaults to time.monotonic.  Pass a fake clock in tests
             to advance time without sleeping.

    Initial state is STOPPED (parado) — lower rate protects the passenger
    if the system starts while the taxi is waiting at a traffic light.
    """

    def __init__(self, now: Callable[[], float] = time.monotonic) -> None:
        self._now = now
        self._state: str = "parado"       # "parado" | "en_marcha"
        self._fare: Decimal = Decimal("0")
        self._last_tick: float = now()

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
        rate = RATE_MOVING if self._state == "en_marcha" else RATE_STOPPED
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
        """Create and return a new Ride."""
        self._current_ride = Ride(now=self._now)
        return self._current_ride

    @property
    def current_ride(self) -> Ride | None:
        return self._current_ride
