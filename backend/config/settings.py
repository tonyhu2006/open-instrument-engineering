"""
Django settings for OpenInstrument project.

Multi-tenant configuration using django-tenants for PostgreSQL schema isolation.
Each project gets its own schema for complete data separation.
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-key-change-in-production")

DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# =============================================================================
# Multi-Tenancy Configuration (django-tenants)
# =============================================================================

# Tenant model configuration
TENANT_MODEL = "tenants.ProjectTenant"
TENANT_DOMAIN_MODEL = "tenants.ProjectDomain"

# Apps that have data in the public schema (shared across all tenants)
SHARED_APPS = [
    "django_tenants",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    # Required for BLACKLIST_AFTER_ROTATION to actually revoke refresh tokens.
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    # Local shared apps (§4.10 / §4.1.12 order)
    "apps.tenants",
    "apps.administration",  # Users, Organizations, Roles, Task forces
    "apps.audit",  # AuditLog (§6.1.1, ADM-07)
    "apps.core",  # abstract base classes, service layer
]

# Apps that have data in tenant schemas (project-specific)
TENANT_APPS = [
    "django.contrib.contenttypes",
    # Third-party apps needed in tenant schema
    "mptt",
    # Local tenant apps
    "apps.core_engineering",  # Tags, Loops, PlantHierarchy are per-project
]

# All installed apps (union of shared and tenant apps)
INSTALLED_APPS = list(SHARED_APPS) + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]

# Custom User Model
AUTH_USER_MODEL = "administration.User"

# Public schema name
PUBLIC_SCHEMA_NAME = "public"

# Show tenant info in admin
SHOW_PUBLIC_IF_NO_TENANT_FOUND = True

MIDDLEWARE = [
    # Tenant middleware must be first
    "apps.tenants.middleware.HeaderBasedTenantMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.tenants.middleware.TenantContextMiddleware",
    "django.middleware.locale.LocaleMiddleware",  # I18N-01 (Accept-Language)
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

# Database - PostgreSQL with django-tenants
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": os.getenv("DB_NAME", "openinstrument"),
        "USER": os.getenv("DB_USER", "openinstrument"),
        "PASSWORD": os.getenv("DB_PASSWORD", "openinstrument_dev_password"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        # Docker PostgreSQL on the non-standard port (AGENTS.md, §5.1.1).
        "PORT": os.getenv("DB_PORT", "5433"),
    }
}

# Cache - Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://localhost:6380/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization (§6.2, I18N-01): English default + 11 languages.
LANGUAGE_CODE = "en-us"
LANGUAGES = [
    ("en", "English"),
    ("zh-hans", "简体中文"),
    ("zh-hant", "繁體中文"),
    ("ja", "日本語"),
    ("ko", "한국어"),
    ("fr", "Français"),
    ("es", "Español"),
    ("it", "Italiano"),
    ("de", "Deutsch"),
    ("ru", "Русский"),
    ("ar", "العربية"),
    ("he", "עברית"),
]
# Frontend language codes (BCP 47) accepted by /api/v1/me/preferences/.
PREFERENCE_LANGUAGES = [
    "en",
    "en-US",
    "zh-CN",
    "zh-TW",
    "ja",
    "ko",
    "fr",
    "es",
    "it",
    "de",
    "ru",
    "ar",
    "he",
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS Configuration
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")

# In DEBUG, allow any localhost / 127.0.0.1 port (covers the Vite dev server,
# the Windsurf browser-preview proxy which uses a random port, etc.).
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://localhost:\d+$",
    r"^http://127\.0\.0\.1:\d+$",
]

CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins — required since Django 4.0 for any non-GET request
# whose Origin/Referer host differs from the server. Wildcard ports are
# supported (Django ≥4.0). Includes all local dev hosts and the Windsurf
# browser-preview proxy (random port on 127.0.0.1 / localhost).
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:*,http://127.0.0.1:*",
).split(",")

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    # Deny by default: views must declare ``rbac_resource`` (§15.2.4) — a view
    # without one is Administrator-only.
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "apps.administration.permissions.IsProjectMemberOrPublicSchema",
        "apps.administration.permissions.RoleMatrixPermission",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # §4.2.1: ?page=&page_size= (default 50, max 500)
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "PAGE_SIZE": 50,
    # §4.2.2 error envelope
    "EXCEPTION_HANDLER": "apps.core.exceptions.api_exception_handler",
}

# Simple JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# DRF Spectacular (OpenAPI)
SPECTACULAR_SETTINGS = {
    "TITLE": "OpenInstrument API",
    "DESCRIPTION": "AI-Driven Instrumentation Design Platform API",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # Disambiguate identically named `status` choice sets across models.
    "ENUM_NAME_OVERRIDES": {
        "ProjectStatusEnum": "apps.tenants.models.ProjectTenant.Status",
        "TagStatusEnum": "apps.core_engineering.models.Tag.Status",
        "NamingEntityTypeEnum": (
            "apps.core_engineering.models.NamingConvention.EntityType"
        ),
        "AuditActionEnum": "apps.audit.models.AuditLog.Action",
    },
}

# =============================================================================
# Logging — capture full tracebacks to logs/django_errors.log so we can
# diagnose 500s even when the runserver stdout is not visible (e.g. detached
# background processes).
# =============================================================================
_LOG_DIR = BASE_DIR / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {process:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(_LOG_DIR / "django_errors.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
