"""
Reproduce the 500 error when creating a ProjectTenant via the admin UI.

Runs in the public schema, simulates exactly what
`ProjectTenantCreateSerializer.save()` does. Prints full traceback on failure.

Usage (from backend/):
    python -m scripts.repro_create_project
"""

from __future__ import annotations

import os
import sys
import traceback
from datetime import date

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection  # noqa: E402
from django_tenants.utils import get_public_schema_name  # noqa: E402

from apps.tenants.models import ProjectTenant  # noqa: E402
from apps.administration.models import Organization  # noqa: E402


def main() -> int:
    # Make sure we're in the public schema (mirror the middleware fix)
    connection.set_schema_to_public()
    print(f"[info] connection schema = {connection.schema_name}")

    # Pick the first organization; bail if none exist
    org = Organization.objects.first()
    if org is None:
        print("[error] no Organization rows exist. Create one first in /admin/.")
        return 1
    print(f"[info] using organization id={org.id} name={org.name!r}")

    # Unique project_no so we don't collide on re-run
    i = 1
    while ProjectTenant.objects.filter(project_no=f"REPRO-{i:03d}").exists():
        i += 1
    project_no = f"REPRO-{i:03d}"
    print(f"[info] will create project_no={project_no}")

    payload = dict(
        project_no=project_no,
        name=f"Repro project {i}",
        organization_id=org.id,
        description="debug reproduction",
        status=ProjectTenant.Status.ACTIVE,
        start_date=date.today(),
    )

    try:
        proj = ProjectTenant(**payload)
        proj.save()  # triggers auto_create_schema + migrations
    except Exception:  # noqa: BLE001
        print("\n[FAILED] exception while saving ProjectTenant:")
        traceback.print_exc()
        return 2

    print(
        f"[OK] created ProjectTenant id={proj.id} "
        f"project_no={proj.project_no} schema_name={proj.schema_name}"
    )

    # Clean up so the script is idempotent
    try:
        proj.delete()  # auto_drop_schema=True will drop the schema
        print(f"[info] cleaned up project {project_no} and its schema")
    except Exception:  # noqa: BLE001
        print("[warn] cleanup failed (non-fatal):")
        traceback.print_exc()
    return 0


if __name__ == "__main__":
    sys.exit(main())
