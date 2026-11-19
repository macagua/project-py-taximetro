"""TaxiTech Solutions — Fleet web panel."""

import reflex as rx
from reflex_django import add_auth_pages
from reflex_django.pages.decorators import page
from reflex_django.auth import login_required

from rxconfig import config


class State(rx.State):
    """App state."""

    @rx.event
    @login_required
    async def logout(self):
        from django.contrib.auth import aget_user, alogout
        await alogout(self.request)
        return rx.redirect("/login")


@page(route="/", login_required=True)
def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading("TaxiTech Solutions — Panel de Flota", size="7"),
            rx.text("Bienvenido. Aquí irá el historial de carreras (US-09)."),
            rx.button(
                "Cerrar sesión",
                on_click=State.logout,
                color_scheme="red",
                size="3",
            ),
            spacing="5",
            padding="2em",
        )
    )


app = rx.App()
app.add_page(index)
add_auth_pages(app)
