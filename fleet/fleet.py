"""TaxiTech Solutions — Fleet web panel."""

import asyncio
import time
from decimal import Decimal, ROUND_HALF_UP

import reflex as rx
from reflex_django import add_auth_pages
from reflex_django.auth import login_required
from reflex_django.pages.decorators import page
from reflex_django.states import AppState

from rxconfig import config
from taximeter.core import RATE_STOPPED, RATE_MOVING
from taximeter import history


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fare_from_segments(
    segments: list[list],
    segment_start: float,
    vehicle_state: str,
) -> Decimal:
    """Recompute total fare from closed segments + the current open segment.

    Uses the same rate constants as core.py — no tick accumulation.
    """
    total = Decimal("0")
    for seg in segments:
        start, end, state = seg
        elapsed = Decimal(str(end - start))
        rate = RATE_MOVING if state == "en_marcha" else RATE_STOPPED
        total += elapsed * rate

    # Current open segment
    now = time.monotonic()
    elapsed = Decimal(str(now - segment_start))
    rate = RATE_MOVING if vehicle_state == "en_marcha" else RATE_STOPPED
    total += elapsed * rate

    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class TaxiState(AppState):
    """Taximeter page state.

    Segments stored as [[start, end, state], ...].
    end = -1.0 signals an open (not yet closed) segment.
    """

    ride_active: bool = False
    vehicle_state: str = "parado"       # "parado" | "en_marcha"
    segments: list[list] = []           # closed segments
    segment_start: float = 0.0          # start of the current open segment
    ride_start: float = 0.0             # ride start for duration_s
    fare_display: str = "0.00"

    # --- ride control ---

    @rx.event
    @login_required
    def start_ride(self):
        now = time.monotonic()
        self.ride_active = True
        self.vehicle_state = "parado"
        self.segments = []
        self.segment_start = now
        self.ride_start = now
        self.fare_display = "0.00"
        return TaxiState.tick

    @rx.event
    @login_required
    def set_moving(self):
        if not self.ride_active or self.vehicle_state == "en_marcha":
            return
        now = time.monotonic()
        self.segments.append([self.segment_start, now, self.vehicle_state])
        self.vehicle_state = "en_marcha"
        self.segment_start = now

    @rx.event
    @login_required
    def set_stopped(self):
        if not self.ride_active or self.vehicle_state == "parado":
            return
        now = time.monotonic()
        self.segments.append([self.segment_start, now, self.vehicle_state])
        self.vehicle_state = "parado"
        self.segment_start = now

    @rx.event
    @login_required
    def finish_ride(self):
        if not self.ride_active:
            return
        fare = _fare_from_segments(
            self.segments, self.segment_start, self.vehicle_state
        )
        duration = time.monotonic() - self.ride_start
        history.save(duration, fare)
        self.fare_display = str(fare)
        self.ride_active = False
        self.segments = []

    @rx.event
    @login_required
    async def logout(self):
        # alogout() tries request.user = AnonymousUser(), which DjangoStateRequest
        # doesn't support (read-only property). Flushing the session directly
        # is the security-critical operation: it invalidates the session ID.
        await self.request.session.aflush()
        return rx.redirect("/login")

    # --- background ticker ---

    @rx.event(background=True)
    async def tick(self):
        while True:
            await asyncio.sleep(1)
            async with self:
                if not self.ride_active:
                    break
                fare = _fare_from_segments(
                    self.segments, self.segment_start, self.vehicle_state
                )
                self.fare_display = str(fare)


# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

def _status_badge() -> rx.Component:
    return rx.badge(
        rx.cond(TaxiState.vehicle_state == "en_marcha", "EN MARCHA", "PARADO"),
        color_scheme=rx.cond(TaxiState.vehicle_state == "en_marcha", "green", "orange"),
        size="3",
        radius="full",
    )


def _fare_display() -> rx.Component:
    return rx.vstack(
        rx.text("Importe actual", size="3", color_scheme="gray"),
        rx.heading(
            TaxiState.fare_display + " €",
            size="9",
            weight="bold",
            color=rx.cond(TaxiState.vehicle_state == "en_marcha", "green", "orange"),
        ),
        align="center",
        spacing="1",
    )


def _ride_buttons() -> rx.Component:
    inactive = ~TaxiState.ride_active
    return rx.hstack(
        rx.button(
            "Parado",
            on_click=TaxiState.set_stopped,
            disabled=rx.cond(inactive | (TaxiState.vehicle_state == "parado"), True, False),
            color_scheme="orange",
            size="4",
            radius="large",
            flex="1",
        ),
        rx.button(
            "En marcha",
            on_click=TaxiState.set_moving,
            disabled=rx.cond(inactive | (TaxiState.vehicle_state == "en_marcha"), True, False),
            color_scheme="green",
            size="4",
            radius="large",
            flex="1",
        ),
        spacing="3",
        width="100%",
    )


def taximeter_page_content() -> rx.Component:
    return rx.container(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Taxímetro", size="6"),
                rx.spacer(),
                rx.button("Salir", on_click=TaxiState.logout, variant="ghost", size="2"),
                width="100%",
            ),
            rx.divider(),

            # State badge (only when ride active)
            rx.cond(TaxiState.ride_active, _status_badge(), rx.text("")),

            # Fare display
            _fare_display(),
            rx.divider(),

            # State-change buttons (enabled only during a ride)
            _ride_buttons(),

            # Iniciar / Finalizar
            rx.cond(
                TaxiState.ride_active,
                rx.button(
                    "Finalizar carrera",
                    on_click=TaxiState.finish_ride,
                    color_scheme="red",
                    size="4",
                    width="100%",
                    radius="large",
                ),
                rx.button(
                    "Iniciar carrera",
                    on_click=TaxiState.start_ride,
                    color_scheme="blue",
                    size="4",
                    width="100%",
                    radius="large",
                ),
            ),

            spacing="5",
            padding="1.5em",
            max_width="480px",
            margin="0 auto",
            width="100%",
        ),
        padding_x="1em",
    )


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@page(route="/", login_required=True)
def index() -> rx.Component:
    return taximeter_page_content()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = rx.App()
app.add_page(index)
add_auth_pages(app)
