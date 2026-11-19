# Guía de instalación — Despliegue con Docker (Fase 4)

Taxímetro Digital — TaxiTech Solutions · `taximeter v0.1.0`

---

## Requisitos previos

| Herramienta | Versión mínima | Instalación |
|---|---|---|
| Docker Engine | 24+ | [docs.docker.com](https://docs.docker.com/engine/install/) |
| Docker Compose | v2 (`compose` plugin) | incluido con Docker Desktop / Engine 24+ |
| Git | 2.x | [git-scm.com](https://git-scm.com/) |

Verificar instalación:

```bash
docker --version          # Docker version 24.x.x
docker compose version    # Docker Compose version v2.x.x
```

---

## 1. Obtener el código

```bash
git clone <url-del-repo>
cd project-py-taximetro
```

---

## 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env`. La única variable obligatoria es `SECRET_KEY`.

> **Importante:** Si la clave contiene el carácter `$`, escápalo como `$$`
> o genera una clave sin ese carácter (ver comando abajo).
> Docker Compose interpola `$` como variables de shell.

Generar una clave segura sin `$`:

```bash
docker run --rm python:3.12-slim python -c "
import secrets, string
chars = string.ascii_letters + string.digits + '!@#%^&*(-_=+)'
print('SECRET_KEY=' + ''.join(secrets.choice(chars) for _ in range(50)))
"
```

Ejemplo de `.env` para producción:

```dotenv
SECRET_KEY=tu-clave-secreta-sin-dolares
DEBUG=False
```

---

## 3. Construir e iniciar

```bash
docker compose up -d
```

Este único comando:

1. Construye la imagen Docker (descarga Python 3.12-slim + uv + dependencias).
2. Compila el frontend de Reflex durante la construcción (~2–5 min la primera vez; las sucesivas usan caché de capas).
3. Al arrancar el contenedor ejecuta automáticamente:
   - `reflex-django migrate` — aplica migraciones pendientes.
   - `reflex-django load_initial_users` — crea los usuarios iniciales si no existen.
   - `reflex-django collectstatic` — copia estáticos del admin.
4. Inicia el servidor Reflex en modo producción.

La aplicación queda disponible en **`http://localhost:3000`**.

---

## 4. Usuarios iniciales

Al primer arranque se crean automáticamente:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `admin` | Superusuario → redirige a `/admin/` |
| `anapoleo` | `c@rolina123` | Staff |
| `leonardo` | `caballero123` | Staff |

> Cambia las contraseñas inmediatamente en `/admin/auth/user/` tras el primer acceso.

---

## 5. URLs disponibles

| URL | Descripción |
|---|---|
| `http://localhost:3000/` | Panel del taxímetro |
| `http://localhost:3000/history` | Historial de carreras |
| `http://localhost:3000/login` | Inicio de sesión |
| `http://localhost:3000/admin/` | Django Admin (Grappelli) |
| `http://localhost:3000/api/docs` | API REST — Swagger UI |

---

## 6. Persistencia de datos

Los datos sobreviven a cualquier reinicio o recreación del contenedor gracias a los volúmenes Docker:

| Volumen | Contenido |
|---|---|
| `taxidata` | Base de datos SQLite (`db.sqlite3`) + historial JSONL heredado |
| `taxilogs` | Logs del taxímetro |

Para ver dónde están montados los volúmenes en el sistema:

```bash
docker volume inspect project-py-taximetro_taxidata
```

---

## 7. Comandos útiles

```bash
# Ver logs en tiempo real
docker compose logs -f app

# Ejecutar un comando de gestión Django dentro del contenedor
docker compose exec app uv run reflex-django createsuperuser
docker compose exec app uv run reflex-django import_jsonl --dry-run

# Abrir una shell dentro del contenedor
docker compose exec app bash

# Parar el contenedor (los datos se conservan)
docker compose down

# Parar y eliminar los volúmenes (¡borra todos los datos!)
docker compose down -v
```

---

## 8. Actualizar a una nueva versión

```bash
git pull
docker compose build          # reconstruye la imagen con el nuevo código
docker compose up -d          # reinicia el contenedor
# Las migraciones nuevas se aplican automáticamente en el arranque.
```

---

## 9. Solución de problemas

### El contenedor no arranca

```bash
docker compose logs app
```

Causas habituales:

| Síntoma | Causa probable | Solución |
|---|---|---|
| `KeyError: 'SECRET_KEY'` | `.env` no existe o está vacío | Crear `.env` con `SECRET_KEY=...` |
| `WARNING: variable is not set` | `SECRET_KEY` contiene `$` | Escapar `$` como `$$` en `.env` |
| Puerto 3000 en uso | Otra aplicación ocupa el puerto | Cambiar `"3000:3000"` en `docker-compose.yml` |
| `unzip: not found` | Imagen sin `unzip` (antigua) | Reconstruir: `docker compose build --no-cache` |

### Reconstruir desde cero

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```
