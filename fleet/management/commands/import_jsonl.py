"""Management command: import ride history from data/rides.jsonl into the DB."""

import json
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils.dateparse import parse_datetime

from fleet.models import Ride


class Command(BaseCommand):
    help = "Importa carreras desde data/rides.jsonl a la base de datos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="data/rides.jsonl",
            help="Ruta al fichero JSONL (por defecto: data/rides.jsonl)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra lo que se importaría sin escribir en la DB.",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"Fichero no encontrado: {path}")

        dry_run = options["dry_run"]
        imported = skipped = 0

        with path.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    fecha = parse_datetime(record["fecha"])
                    duracion_s = float(record["duracion_s"])
                    total_eur = Decimal(record["total_eur"])
                except Exception as exc:
                    self.stderr.write(f"  Línea {lineno} ignorada: {exc}")
                    skipped += 1
                    continue

                if not dry_run:
                    Ride.objects.get_or_create(
                        fecha=fecha,
                        defaults={"duracion_s": duracion_s, "total_eur": total_eur},
                    )
                else:
                    self.stdout.write(f"  [dry-run] {fecha}  {total_eur} €")
                imported += 1

        verb = "se importarían" if dry_run else "importadas"
        self.stdout.write(
            self.style.SUCCESS(f"{imported} carrera(s) {verb}, {skipped} ignoradas.")
        )
