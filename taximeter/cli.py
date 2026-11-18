"""Terminal interface for the taximeter."""

from string import Template
from taximeter.core import Taximeter
import taximeter

_BANNER = """
==================================================
  $title
==================================================
  Comandos disponibles:
    [s]  Iniciar carrera
    [q]  Salir del programa
==================================================
"""

_RIDE_HEADER = """
--- Carrera iniciada ---
Estado: PARADO
(próxima historia: comandos p / m / f)
"""


def show_banner() -> None:
    """Show Menu banner"""
    print(
        Template(_BANNER).substitute(
            title=taximeter.__doc__
        )
    )


def ride_loop(ride) -> None:
    """Inner loop for an active ride.

    US-01 stub: returns after one Enter press.
    US-02 will replace the body with p / m / f commands.
    """
    print(_RIDE_HEADER)
    input("Pulsa Enter para volver al menú principal... ")


def main_loop(taximeter: Taximeter) -> None:
    """Main loop for the taximeter application.

    Args:
        taximeter (Taximeter): Taximeter instance to manage the ride process.
    """
    while True:
        try:
            cmd = input("Comando> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nCerrando taxímetro. ¡Hasta pronto!")
            break

        if cmd == "s":
            ride = taximeter.start_ride()
            ride_loop(ride)
        elif cmd == "q":
            print("Cerrando taxímetro. ¡Hasta pronto!")
            break
        else:
            print(f"Comando '{cmd}' no reconocido. Opciones: s (iniciar), q (salir)")


def main() -> None:
    """Main program"""
    # Show banner and start the main loop
    show_banner()
    # Create an instance of Taximeter and run the main
    main_loop(Taximeter())
