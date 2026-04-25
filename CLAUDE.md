# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack & layout

Monorepo with `backend/` (Django 5.2 + DRF, Python ≥3.11, managed by `uv`) and `frontend/` (React 19 + TypeScript + Vite 7 + Tailwind v4 + Shadcn UI). PostgreSQL 16 and Redis 7 run via `docker-compose.yml` on **non-standard ports 5433 and 6380** (so they don't collide with local installs). License is AGPL-3.0 (the README badge says MIT — ignore it).

Project documentation lives in `docs/` and is more current than the README:
- `docs/SPECIFICATION.md` — architecture & data model spec
- `docs/IMPLEMENTATION.md` — what's actually built
- `docs/DEVELOPMENT_ROADMAP.md` — version history & roadmap
- `docs/PRD.md` — product requirements

## Common commands

Infrastructure (must be running before backend):
```bash
docker-compose up -d        # postgres on 5433, redis on 6380
```

Backend (run from `backend/`):
```bash
uv sync                                       # install deps
uv run python manage.py migrate_schemas --shared    # migrate public schema (django-tenants)
uv run python manage.py migrate_schemas             # migrate all tenant schemas
uv run python manage.py seed_demo_data        # tenant-schema demo data (engineering)
uv run python manage.py seed_admin_data       # public-schema demo data (orgs, users, roles)
uv run python manage.py runserver             # http://localhost:8000
uv run pytest                                 # tests (pytest-django; no config file yet)
uv run ruff check .                           # lint
uv run black .                                # format
```

Note: because of `django-tenants`, prefer `migrate_schemas` over `migrate`. Plain `migrate` only touches the public schema.

Frontend (run from `frontend/`):
```bash
npm install
npm run dev      # http://localhost:5173, proxies /api → http://localhost:8000
npm run build    # tsc -b && vite build
npm run lint     # eslint
```

API docs: `/api/docs/` (Swagger), `/api/redoc/`, `/api/schema/` (raw OpenAPI).

## Architecture: multi-tenancy is the central design constraint

This codebase uses **`django-tenants` with a PostgreSQL schema per project**. Understanding the shared/tenant split is essential — putting a model in the wrong place will break migrations or cross-schema queries.

**Two app categories** in `backend/config/settings.py`:

- `SHARED_APPS` (live in `public` schema, visible to all tenants):
  `apps.core`, `apps.tenants`, `apps.administration` (Users, Organizations, Roles, AuditLog, ProjectMembership, ProjectTaskForce).
- `TENANT_APPS` (live in per-project schemas, isolated):
  `apps.core_engineering` (Client, Site, Plant, PlantHierarchy, NamingConvention, Tag, Loop, InstrumentType).

**Tenant model**: `apps.tenants.ProjectTenant` (each Project = one tenant). `schema_name` is auto-derived from `project_no` in `ProjectTenant.save()`. `auto_create_schema=True` means saving a new ProjectTenant immediately provisions a schema.

**Tenant selection**: `apps.tenants.middleware.HeaderBasedTenantMiddleware` switches schemas based on the **`X-Project-ID`** request header (no subdomains). Requests under `/admin/` and `/api/token` always use the public schema. Without the header, public schema is used (suitable for shared resources like auth).

**Cross-schema FK rule**: tenant-schema models cannot have ForeignKeys to shared-schema models, and shared-schema models cannot FK into tenant schemas. The codebase works around this by storing **`project_id` as a plain `IntegerField`** (see `ProjectMembership`, `ProjectTaskForce`, `AuditLog` in `apps/administration/models.py`) and exposing a `project` property that does an explicit lookup. Follow this pattern for new cross-schema references — don't add a real FK.

**Custom user**: `AUTH_USER_MODEL = "administration.User"` (extends `AbstractUser` with org/role/language/timezone/avatar). Always reference via `settings.AUTH_USER_MODEL`, not a direct import.

**Auth**: JWT via `rest_framework_simplejwt` at `/api/token/` and `/api/token/refresh/`. Default DRF permission is `IsAuthenticated`. `PAGE_SIZE = 50`.

**RBAC**: 5 levels in `Role.Level` (1 Guest → 5 Administrator). Admins bypass permission checks in `User.has_permission`. Non-admin permissions are stored as a JSON matrix `{model_name: [actions]}` on `Role.permissions`.

**Plant hierarchy** uses `django-mptt` (`PlantHierarchy` is an MPTT tree of Plant → Area → Unit nodes inside the tenant schema).

## Frontend architecture

React Router 7 SPA, client-side auth via Zustand (`src/stores/authStore.ts`), JWT stored in `localStorage` (`access_token` / `refresh_token`). `ProtectedRoute` wraps the authenticated layout. Vite alias **`@` → `src`**.

API base path is `/api` and is proxied to `http://localhost:8000` by Vite's dev server (see `vite.config.ts`). The frontend must send the `X-Project-ID` header for any tenant-scoped request to hit the right schema.

Key directories: `components/{auth,hierarchy,layout,table,ui}`, `pages/`, `contexts/`, `stores/`.

**Heads up — missing `src/lib/`**: a dozen files import `@/lib/api` (the API client) and `@/lib/utils` (the Shadcn `cn` helper), but `frontend/src/lib/` does not exist on this branch. Frontend builds will fail until those modules are created. If you're touching the frontend, expect to either create these files or be working in a partial state.

## Conventions worth knowing

- All models inherit `apps.core.models.TimeStampedModel` for `created_at` / `updated_at`.
- Engineering URL routes are mounted at `/api/engineering/` (tags, loops, instrument-types, hierarchy, clients, sites, plants, naming-conventions). Admin/tenant management is at `/api/admin/` and `/api/tenants/`.
- New tenant-schema migrations require running `migrate_schemas` (not `migrate`) so every existing tenant gets the change. Adding `auto_create_schema=True` means new `ProjectTenant` rows trigger schema creation at save time — be careful in tests.
- Ruff config: `line-length = 88`, rules `E,F,I,N,W`. Black also at 88.
