import reflex as rx
from reflex_django.plugins import ReflexDjangoPlugin

config = rx.Config(
    app_name="fleet",
    plugins=[
        ReflexDjangoPlugin(
            config={
                "settings_module": "fleet.settings",
                "profile": "integrated",
            }
        ),
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(appearance="light", accent_color="blue", radius="medium")
        ),
    ],
)
