"""Terminal interface for the taximeter."""

from string import Template
from taximeter.core import Taximeter
from taximeter import history, logs
import taximeter

_BANNER = """
==================================================
  $title
==================================================
  Comandos disponibles:
    [s]  Iniciar carrera
    [h]  Historial de hoy
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
    print(Template(_BANNER).substitute(title=taximeter.__doc__))


def ride_loop(ride) -> None:
    """Inner loop for an active ride: p / m / f commands."""
    log = logs.get()
    log.info("Carrera iniciada")
    print(_RIDE_BANNER)
    while True:
        try:
            cmd = input("Carrera> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            log.warning("Carrera interrumpida por el usuario")
            print("\nCarrera interrumpida.")
            return

        if cmd == "m":
            if ride.set_moving():
                log.info("Estado → EN MARCHA")
                print("  EN MARCHA  (0.05 €/s)")
            else:
                log.debug("Comando m redundante (ya en marcha)")
                print("  Ya estás en marcha.")
        elif cmd == "p":
            if ride.set_stopped():
                log.info("Estado → PARADO")
                print("  PARADO     (0.02 €/s)")
            else:
                log.debug("Comando p redundante (ya parado)")
                print("  Ya estás parado.")
        elif cmd == "f":
            try:
                total = ride.finish()
                history.save(ride.duration_s, total)
            except Exception:
                log.exception("Error al finalizar carrera")
                print("  Error al guardar la carrera. Consulta el log.")
                return
            log.info(
                "Carrera finalizada — duración %.1f s, total %s €",
                ride.duration_s,
                total,
            )
            print(f"\n  Total: {total} €\n")
            return
        else:
            log.debug("Comando desconocido en carrera: %r", cmd)
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
        elif cmd == "h":
            count, total = history.summary_today()
            if count == 0:
                print("  Sin carreras hoy.")
            else:
                print(f"\n  Carreras hoy: {count}  |  Total acumulado: {total} €\n")
                for i, r in enumerate(history.rides_today(), 1):
                    print(
                        f"  {i}. {r['fecha']}  {r['duracion_s']} s  {r['total_eur']} €"
                    )
                print()
        elif cmd == "q":
            print("Cerrando taxímetro. ¡Hasta pronto!")
            break
        else:
            print(
                f"Comando '{cmd}' no reconocido. Opciones: s (iniciar), h (historial), q (salir)"
            )


def _django_authenticate() -> bool:
    """Authenticate the operator via Django before starting the CLI.

    Returns True if authentication succeeded, False otherwise.
    Skips auth entirely if Django is not configured (no DJANGO_SETTINGS_MODULE
    and the fleet settings cannot be loaded) so the CLI still works without Django.
    """
    import getpass
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fleet.settings")

    try:
        import dotenv

        dotenv.load_dotenv()
    except ImportError:
        pass  # python-dotenv optional; SECRET_KEY must be set some other way

    try:
        import django

        django.setup()
    except Exception as exc:
        logs.get().warning("Django no disponible, omitiendo autenticación: %s", exc)
        return True  # let the CLI work without Django

    from django.contrib.auth import authenticate

    print("Acceso restringido. Introduce tus credenciales.")
    for attempt in range(3):
        username = input("Usuario: ").strip()
        password = getpass.getpass("Contraseña: ")
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            logs.get().info("Acceso concedido: %s", username)
            print(f"Bienvenido, {username}.\n")
            return True
        remaining = 2 - attempt
        msg = "Credenciales incorrectas."
        if remaining:
            msg += f" Intentos restantes: {remaining}."
        print(msg)
        logs.get().warning("Intento fallido de acceso para usuario: %r", username)

    logs.get().error("Acceso denegado tras 3 intentos fallidos")
    print("Acceso denegado.")
    return False


def main() -> None:
    """Main program"""
    logs.setup()
    logs.get().info("Taxímetro arrancado")
    if not _django_authenticate():
        return
    show_banner()
    main_loop(Taximeter())
    logs.get().info("Taxímetro cerrado")
