"""Tests for taximeter.core — fare calculation logic."""

from decimal import Decimal
from taximeter.core import Ride


def make_ride(*ticks: float) -> Ride:
    """Return a Ride with a fake clock that yields ticks in sequence."""
    clock = iter(ticks)
    return Ride(now=lambda: next(clock))


class TestRideStopped:
    def test_fare_pure_stopped(self):
        # 10 seconds stopped: 10 * 0.02 = 0.20 €
        ride = make_ride(0.0, 10.0)
        assert ride.finish() == Decimal("0.20")

    def test_initial_state_is_parado(self):
        ride = make_ride(0.0)
        assert ride.state == "parado"


class TestRideMoving:
    def test_fare_pure_moving(self):
        # 10 seconds moving: 10 * 0.05 = 0.50 €
        ride = make_ride(0.0, 10.0)
        ride.set_moving()
        # consume the tick inside set_moving, need one more for finish
        ride2 = make_ride(0.0, 0.0, 10.0)
        ride2.set_moving()
        assert ride2.finish() == Decimal("0.50")

    def test_set_moving_changes_state(self):
        ride = make_ride(0.0, 1.0)
        changed = ride.set_moving()
        assert changed is True
        assert ride.state == "en_marcha"


class TestRideMixed:
    def test_stopped_then_moving(self):
        # 5s stopped (0.10) + 5s moving (0.25) = 0.35 €
        # clock: init=0, set_moving ticks at 5, finish ticks at 10
        ride = make_ride(0.0, 5.0, 10.0)
        ride.set_moving()
        assert ride.finish() == Decimal("0.35")

    def test_moving_then_stopped(self):
        # 5s moving (0.25) + 5s stopped (0.10) = 0.35 €
        # clock: init=0, set_moving=0 (no tick, already parado→en_marcha at t=0)
        # Actually: init=0, set_moving ticks at 0 (0s stopped=0€), set_stopped ticks at 5 (5s moving=0.25€), finish at 10 (5s stopped=0.10€)
        ride = make_ride(0.0, 0.0, 5.0, 10.0)
        ride.set_moving()   # ticks: 0→0, state→en_marcha
        ride.set_stopped()  # ticks: 0→5, state→parado
        assert ride.finish() == Decimal("0.35")


class TestRedundantCommand:
    def test_redundant_stopped_returns_false(self):
        ride = make_ride(0.0)
        assert ride.set_stopped() is False
        assert ride.state == "parado"

    def test_redundant_moving_returns_false(self):
        # init at 0, set_moving at 0 (no-op tick), second set_moving redundant
        ride = make_ride(0.0, 0.0, 0.0)
        ride.set_moving()
        assert ride.set_moving() is False
        assert ride.state == "en_marcha"

    def test_redundant_does_not_change_fare(self):
        # 10s stopped, then redundant set_stopped — fare should still be 10*0.02
        ride = make_ride(0.0, 10.0, 10.0)
        ride.set_stopped()   # redundant — returns False, no tick
        assert ride.finish() == Decimal("0.20")


class TestRounding:
    def test_round_half_up_not_half_even(self):
        # 0.1s moving: 0.1 * 0.05 = 0.005
        # ROUND_HALF_UP → 0.01; ROUND_HALF_EVEN → 0.00 (rounds to even)
        ride = make_ride(0.0, 0.0, 0.1)
        ride.set_moving()   # ticks at 0 (0s stopped = 0€), state→en_marcha
        assert ride.finish() == Decimal("0.01")

    def test_finish_returns_two_decimal_places(self):
        # Verify the Decimal always has exactly 2 decimal places
        ride = make_ride(0.0, 1.0)
        total = ride.finish()
        assert total == total.quantize(Decimal("0.01"))
        assert str(total) == "0.02"
