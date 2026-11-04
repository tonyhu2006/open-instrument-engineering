# CLAUDE.md
先读根目录AGENTS.md(跨agent行为契约),本文件仅补充Claude Code特有事项。

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
uv run pytest                                 # tests (pytest-django; config in pyproject.toml)
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

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **Open Instrument** (636 symbols, 1325 relationships, 45 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/Open Instrument/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/Open Instrument/context` | Codebase overview, check index freshness |
| `gitnexus://repo/Open Instrument/clusters` | All functional areas |
| `gitnexus://repo/Open Instrument/processes` | All execution flows |
| `gitnexus://repo/Open Instrument/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
