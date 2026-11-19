"""Django settings for the fleet Reflex-Django app."""

import os
from pathlib import Path
import taximeter

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; SECRET_KEY must be set via the environment

BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY must come from the environment / .env — never hard-coded
SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "grappelli",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "reflex_django",
    "fleet",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # AsyncStreamingMiddleware must be last
    "reflex_django.bridge.streaming.AsyncStreamingMiddleware",
]

ROOT_URLCONF = "fleet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "fleet" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # DB_PATH env var lets Docker mount the file on a persistent volume.
        # Falls back to db.sqlite3 in the project root for local development.
        "NAME": Path(os.environ.get("DB_PATH", str(BASE_DIR / "db.sqlite3"))),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-es"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Reflex-Django auth — no public registration
RX_AUTH = {
    "LOGIN_URL": "/login",
    "SIGNUP_URL": "/signup",
    "LOGIN_REDIRECT_URL": "/",
    "LOGOUT_REDIRECT_URL": "/login",
    "LOGIN_FIELDS": ["username"],
    "PASSWORD_MIN_LENGTH": 8,
    "SIGNUP_ENABLED": False,       # users created with createsuperuser only
    "PASSWORD_RESET_ENABLED": False,
}

# Required by reflex-django built-in login (sets sessionid via JS)
SESSION_COOKIE_HTTPONLY = False

GRAPPELLI_ADMIN_TITLE = taximeter.__doc__
