"""
Shared pytest fixtures for cross-app / tenant-aware tests.

Creating a ProjectTenant runs CREATE SCHEMA + all tenant migrations, which is
slow, so the two isolation tenants are created once per test session (outside
the per-test transaction) and dropped at the end. Per-test data (users, task
forces, extra rows) is created inside the usual pytest-django transaction and
rolled back automatically.
"""

from types import SimpleNamespace

import pytest
from django.db import connection
from django_tenants.utils import schema_context

from apps.administration.models import Organization
from apps.core_engineering.models import Client
from apps.tenants.models import ProjectTenant


@pytest.fixture(scope="session")
def isolation_tenants(django_db_setup, django_db_blocker):
    """Two independent project tenants (A, B), each seeded with one Client.

    Both clients deliberately share the same unique `code` to prove that
    uniqueness is enforced per schema, not globally.
    """
    with django_db_blocker.unblock():
        connection.set_schema_to_public()
        org = Organization.objects.create(code="ISO-ORG", name="Isolation Org")
        tenants = {}
        for key in ("a", "b"):
            tenant = ProjectTenant(
                project_no=f"ISO-{key.upper()}",
                name=f"Isolation Project {key.upper()}",
                organization_id=org.id,
            )
            tenant.save(verbosity=0)
            with schema_context(tenant.schema_name):
                Client.objects.create(code="SHARED", name=f"Client of {key.upper()}")
            tenants[key] = tenant

    yield SimpleNamespace(org=org, **tenants)

    with django_db_blocker.unblock():
        connection.set_schema_to_public()
        for tenant in tenants.values():
            tenant.delete(force_drop=True)
        org.delete()


@pytest.fixture(autouse=True)
def _reset_schema_to_public():
    """The tenant middleware leaves the shared connection on the last
    requested schema; reset around every test so ORM calls start in public."""
    connection.set_schema_to_public()
    yield
    connection.set_schema_to_public()
