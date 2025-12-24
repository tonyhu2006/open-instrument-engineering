# OpenInstrument Backend

Django REST API for the OpenInstrument platform.

## Setup

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

## API Endpoints

- `/api/health/` - Health check endpoint
- `/api/docs/` - Swagger UI documentation
- `/api/redoc/` - ReDoc documentation
