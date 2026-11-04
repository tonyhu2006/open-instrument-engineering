import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db import connection

from apps.tenants.models import ProjectTenant

for t in ProjectTenant.objects.all():
    try:
        connection.set_tenant(t)
        with connection.cursor() as c:
            c.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname = %s AND tablename LIKE 'core_engineering%%'",
                [t.schema_name],
            )
            tables = [row[0] for row in c.fetchall()]
            print(f"{t.project_no} ({t.schema_name}): {len(tables)} tables")
            for tbl in tables:
                print(f"  - {tbl}")
    except Exception as e:
        print(f"{t.project_no} ({t.schema_name}): ERROR - {e}")
    finally:
        connection.set_schema_to_public()
