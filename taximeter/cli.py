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

_RIDE_BANNER = """
--- Carrera iniciada (estado: PARADO) ---
  [m]  En marcha  (0.05 €/s)
  [p]  Parado     (0.02 €/s)
  [f]  Finalizar carrera
"""


def show_banner() -> None:
    """Show Menu banner"""
    print(
        Template(_BANNER).substitute(
            title=taximeter.__doc__
        )
    )


def ride_loop(ride) -> None:
    """Inner loop for an active ride: p / m / f commands."""
    print(_RIDE_BANNER)
    while True:
        try:
            cmd = input("Carrera> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nCarrera interrumpida.")
            return

        if cmd == "m":
            if ride.set_moving():
                print("  EN MARCHA  (0.05 €/s)")
            else:
                print("  Ya estás en marcha.")
        elif cmd == "p":
            if ride.set_stopped():
                print("  PARADO     (0.02 €/s)")
            else:
                print("  Ya estás parado.")
        elif cmd == "f":
            total = ride.finish()
            print(f"\n  Total: {total} €\n")
            return
        else:
            print(f"  Comando '{cmd}' no reconocido. Opciones: m, p, f")


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
            print("Nueva carrera [s]  |  Salir [q]")
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
