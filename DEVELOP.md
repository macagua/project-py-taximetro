# Guía de desarrollo

Taxímetro Digital — TaxiTech Solutions · `taximeter v0.1.0`

---

## Requisitos previos

| Herramienta | Versión mínima | Instalación |
|---|---|---|
| Python | 3.12 | [python.org](https://www.python.org/downloads/) |
| uv | 0.11+ | `pip install uv` o [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Git | 2.x | [git-scm.com](https://git-scm.com/) |
| Node.js / Bun | — | Reflex lo descarga automáticamente en el primer arranque |

---

## Configuración inicial

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd project-py-taximetro
```

### 2. Crear el entorno virtual e instalar dependencias

```bash
uv sync
```

Esto crea `.venv/` con Python 3.12 y todas las dependencias del `uv.lock`.

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` y establece al menos `SECRET_KEY`:

```bash
# Generar una clave segura (sin '$' para compatibilidad con Docker Compose):
uv run python -c "
import secrets, string
chars = string.ascii_letters + string.digits + '!@#%^&*(-_=+)'
print('SECRET_KEY=' + ''.join(secrets.choice(chars) for _ in range(50)))
"
```

Sustituye el valor en `.env`:

```dotenv
SECRET_KEY=<clave-generada>
DEBUG=True
```

### 4. Aplicar migraciones y cargar datos iniciales

```bash
uv run reflex-django migrate
uv run reflex-django load_initial_users
```

Usuarios precargados:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin` | Superusuario |
| `anapoleo` | `c@rolina123` | Staff |
| `leonardo` | `caballero123` | Staff |

### 5. Instalar los hooks de pre-commit

```bash
uv run pre-commit install
```

Para ejecutarlos manualmente sobre todos los ficheros:

```bash
uv run pre-commit run --all-files
```

Hooks activos:

| Hook | Qué verifica |
|---|---|
| `trailing-whitespace`, `end-of-file-fixer` | Limpieza de ficheros |
| `check-yaml`, `check-toml` | Sintaxis de configuración |
| `check-merge-conflict` | Marcadores `<<<` sin resolver |
| `debug-statements` | `breakpoint()` / `pdb` olvidados |
| `ruff` | Linting Python + autofix |
| `ruff-format` | Formato black-compatible |
| `django-check` | `manage.py check` — modelos, URLs, settings |
| `reflex-compile` | Compilación en seco del frontend |
| `pytest-fast` | Tests de core y config |

---

## Arrancar el servidor de desarrollo

```bash
uv run reflex run --env prod --single-port
```

La primera vez Reflex descarga Bun y compila el frontend (~30 s).
Los arranques siguientes son inmediatos.

---

## URLs disponibles

### Reflex (panel web)

| Ruta | Descripción | Autenticación |
|---|---|---|
| `/` | Panel del taxímetro | Requerida |
| `/history` | Historial de carreras con filtro por fecha | Requerida |
| `/login` | Formulario de inicio de sesión | — |

> Los superusuarios y miembros del grupo **Responsables** son redirigidos a `/admin/` al iniciar sesión.

### Django Admin

| Ruta | Descripción |
|---|---|
| `/admin/` | Panel de administración (Grappelli) |
| `/grappelli/` | Assets de la interfaz Grappelli |

### Django-Ninja — API REST

Base: `/api/`  ·  Documentación interactiva: `/api/docs`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/rides` | Iniciar una carrera (devuelve `id`) |
| `PATCH` | `/api/rides/{id}/state` | Cambiar estado del vehículo (`parado` / `en_marcha`) |
| `POST` | `/api/rides/{id}/finish` | Finalizar carrera (`duracion_s`, `total_eur`) |
| `GET` | `/api/rides?date=YYYY-MM-DD` | Listar carreras finalizadas de una fecha |

Todas las rutas requieren sesión Django activa (`django_auth`).

---

## Ejecutar los tests

```bash
# Suite completa
uv run pytest tests/ -v

# Solo tests rápidos (sin BD)
uv run pytest tests/test_core.py tests/test_config.py -q

# Tests de la API REST
uv run pytest tests/test_api.py -v
```

---

## Comandos de gestión útiles

```bash
# Crear superusuario interactivo
uv run reflex-django createsuperuser

# Importar historial desde JSONL a la BD
uv run reflex-django import_jsonl --dry-run   # previsualizar
uv run reflex-django import_jsonl             # importar

# Cargar usuarios iniciales (idempotente)
uv run reflex-django load_initial_users

# Shell de Django
uv run reflex-django shell

# Recopilar estáticos (necesario para producción)
uv run reflex-django collectstatic --noinput
```

---

## Integración continua (GitHub Actions)

El workflow `.github/workflows/pre-commit.yml` ejecuta todos los hooks en cada
`push` y `pull_request`. Configura el secreto `SECRET_KEY` en:

```
GitHub → Settings → Secrets and variables → Actions → New repository secret
```
