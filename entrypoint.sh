#!/bin/sh
set -e

echo "→ Migraciones de base de datos..."
uv run reflex django migrate --noinput

echo "→ Archivos estáticos (admin/grappelli)..."
uv run reflex django collectstatic --noinput --clear -v 0

echo "→ Iniciando Taxímetro Digital..."
exec uv run reflex run --env prod --single-port
