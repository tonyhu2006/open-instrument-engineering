"""
V6 — tenant isolation regression suite (AGENTS.md 验证协议 V6).

Covers three layers:
1. Schema-level data isolation (ORM): rows, constraints and tables live in
   exactly one project schema.
2. Static model contract (AGENTS.md hard rules 1 & 2): tenant models carry no
   project/domain columns and no ForeignKey into shared (public) models.
3. HTTP routing & access control (SPECIFICATION §3.1.0.5.6): X-Project-ID
   selects the schema, and only administrators or project task-force members
   may read a project's data — for both JWT and session authentication.
"""

import pytest
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import schema_context
from rest_framework_simplejwt.tokens import RefreshToken

from apps.administration.models import ProjectTaskForce, TaskForceMembership
from apps.core_engineering.models import Client

pytestmark = pytest.mark.django_db

CLIENTS_URL = "/api/engineering/clients/"
PROJECTS_URL = "/api/tenants/projects/"

User = get_user_model()


# =============================================================================
# Helpers / fixtures
# =============================================================================


def _bearer(user):
    return {"HTTP_AUTHORIZATION": f"Bearer {RefreshToken.for_user(user).access_token}"}


def _project(tenant):
    return {"HTTP_X_PROJECT_ID": str(tenant.pk)}


def _client_names(response):
    data = response.json()
    rows = data["results"] if isinstance(data, dict) else data
    return sorted(row["name"] for row in rows)


@pytest.fixture
def admin_user(isolation_tenants):
    return User.objects.create_user(
        username="iso_admin", password="x", is_superuser=True
    )


@pytest.fixture
def member_of_a(isolation_tenants):
    """Regular user who belongs to project A only (via a task force)."""
    user = User.objects.create_user(
        username="iso_member_a", password="x", organization=isolation_tenants.org
    )
    task_force = ProjectTaskForce.objects.create(
        project_id=isolation_tenants.a.pk, code="TF-A", name="Task Force A"
    )
    TaskForceMembership.objects.create(user=user, task_force=task_force)
    return user


@pytest.fixture
def outsider(isolation_tenants):
    """Authenticated user without membership in any project."""
    return User.objects.create_user(
        username="iso_outsider", password="x", organization=isolation_tenants.org
    )


# =============================================================================
# 1. Schema-level data isolation
# =============================================================================


class TestSchemaIsolation:
    def test_each_schema_only_sees_its_own_rows(self, isolation_tenants):
        with schema_context(isolation_tenants.a.schema_name):
            assert list(Client.objects.values_list("name", flat=True)) == [
                "Client of A"
            ]
        with schema_context(isolation_tenants.b.schema_name):
            assert list(Client.objects.values_list("name", flat=True)) == [
                "Client of B"
            ]

    def test_unique_constraints_are_scoped_to_the_schema(self, isolation_tenants):
        for tenant in (isolation_tenants.a, isolation_tenants.b):
            with schema_context(tenant.schema_name):
                assert Client.objects.filter(code="SHARED").count() == 1

    def test_writes_in_one_schema_do_not_leak(self, isolation_tenants):
        with schema_context(isolation_tenants.a.schema_name):
            Client.objects.create(code="ONLY-A", name="Only in A")
        with schema_context(isolation_tenants.b.schema_name):
            assert not Client.objects.filter(code="ONLY-A").exists()

    def test_tenant_tables_do_not_exist_in_public_schema(self, isolation_tenants):
        table = Client._meta.db_table

        def table_exists(schema):
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema = %s AND table_name = %s",
                    [schema, table],
                )
                return cursor.fetchone() is not None

        assert not table_exists("public")
        assert table_exists(isolation_tenants.a.schema_name)
        assert table_exists(isolation_tenants.b.schema_name)


# =============================================================================
# 2. Static model contract (AGENTS.md hard rules 1 & 2)
# =============================================================================


def _local_tenant_models():
    labels = {
        apps.get_containing_app_config(name).label
        for name in settings.TENANT_APPS
        if name.startswith("apps.")
    }
    return [m for label in labels for m in apps.get_app_config(label).get_models()]


def _tenant_only_labels():
    shared = {apps.get_containing_app_config(n).label for n in settings.SHARED_APPS}
    tenant = {apps.get_containing_app_config(n).label for n in settings.TENANT_APPS}
    # contenttypes lives in both schemas by design, so FKs to it are safe.
    return (tenant - shared) | {"contenttypes"}


class TestTenantModelContract:
    def test_tenant_models_exist(self):
        assert _local_tenant_models(), "No local TENANT_APPS models discovered"

    def test_tenant_models_have_no_project_or_domain_columns(self):
        offenders = [
            f"{model.__name__}.{field.name}"
            for model in _local_tenant_models()
            for field in model._meta.concrete_fields
            if field.column in {"project_id", "domain_id"}
        ]
        assert offenders == [], f"Tenant models must not scope by column: {offenders}"

    def test_tenant_models_have_no_fk_into_shared_schema(self):
        allowed = _tenant_only_labels()
        offenders = [
            f"{model.__name__}.{field.name} -> {field.related_model._meta.label}"
            for model in _local_tenant_models()
            for field in model._meta.get_fields()
            if field.is_relation
            and field.concrete
            and field.related_model is not None
            and field.related_model._meta.app_label not in allowed
        ]
        assert offenders == [], f"Cross-schema ForeignKeys found: {offenders}"


# =============================================================================
# 3. HTTP routing & access control
# =============================================================================


class TestTenantRouting:
    def test_admin_sees_only_the_selected_projects_data(
        self, client, admin_user, isolation_tenants
    ):
        auth = _bearer(admin_user)
        resp_a = client.get(CLIENTS_URL, **auth, **_project(isolation_tenants.a))
        resp_b = client.get(CLIENTS_URL, **auth, **_project(isolation_tenants.b))
        assert resp_a.status_code == 200
        assert resp_b.status_code == 200
        assert _client_names(resp_a) == ["Client of A"]
        assert _client_names(resp_b) == ["Client of B"]

    def test_unknown_project_id_returns_404(self, client, admin_user):
        resp = client.get(
            CLIENTS_URL, **_bearer(admin_user), HTTP_X_PROJECT_ID="999999"
        )
        assert resp.status_code == 404


class TestTenantAccessControl:
    def test_member_can_read_own_project(self, client, member_of_a, isolation_tenants):
        resp = client.get(
            CLIENTS_URL, **_bearer(member_of_a), **_project(isolation_tenants.a)
        )
        assert resp.status_code == 200
        assert _client_names(resp) == ["Client of A"]

    def test_member_cannot_read_foreign_project_via_jwt(
        self, client, member_of_a, isolation_tenants
    ):
        resp = client.get(
            CLIENTS_URL, **_bearer(member_of_a), **_project(isolation_tenants.b)
        )
        assert resp.status_code == 403
        assert "Client of B" not in resp.content.decode()

    def test_member_cannot_read_foreign_project_via_session(
        self, client, member_of_a, isolation_tenants
    ):
        client.force_login(member_of_a)
        resp = client.get(CLIENTS_URL, **_project(isolation_tenants.b))
        assert resp.status_code == 403
        assert "Client of B" not in resp.content.decode()

    def test_user_without_membership_cannot_read_any_project(
        self, client, outsider, isolation_tenants
    ):
        for tenant in (isolation_tenants.a, isolation_tenants.b):
            resp = client.get(CLIENTS_URL, **_bearer(outsider), **_project(tenant))
            assert resp.status_code == 403, tenant.project_no

    def test_anonymous_cannot_read_project_data(self, client, isolation_tenants):
        resp = client.get(CLIENTS_URL, **_project(isolation_tenants.a))
        assert resp.status_code in (401, 403)
        assert "Client of A" not in resp.content.decode()

    def test_member_cannot_write_into_foreign_project(
        self, client, member_of_a, isolation_tenants
    ):
        resp = client.post(
            CLIENTS_URL,
            {"code": "INTRUDER", "name": "Intruder"},
            content_type="application/json",
            **_bearer(member_of_a),
            **_project(isolation_tenants.b),
        )
        assert resp.status_code == 403
        with schema_context(isolation_tenants.b.schema_name):
            assert not Client.objects.filter(code="INTRUDER").exists()


class TestProjectVisibility:
    def _project_nos(self, response):
        data = response.json()
        rows = data["results"] if isinstance(data, dict) else data
        return {row["project_no"] for row in rows}

    def test_member_lists_only_own_projects(self, client, member_of_a):
        resp = client.get(PROJECTS_URL, **_bearer(member_of_a))
        assert resp.status_code == 200
        assert self._project_nos(resp) == {"ISO-A"}

    def test_user_without_membership_lists_no_projects(self, client, outsider):
        resp = client.get(PROJECTS_URL, **_bearer(outsider))
        assert resp.status_code == 200
        assert self._project_nos(resp) == set()

    def test_admin_lists_all_projects(self, client, admin_user):
        resp = client.get(PROJECTS_URL, **_bearer(admin_user))
        assert resp.status_code == 200
        assert {"ISO-A", "ISO-B"} <= self._project_nos(resp)

    def test_public_only_routes_ignore_forged_project_header(
        self, client, member_of_a, isolation_tenants
    ):
        resp = client.get(
            PROJECTS_URL, **_bearer(member_of_a), **_project(isolation_tenants.b)
        )
        assert resp.status_code == 200
        assert self._project_nos(resp) == {"ISO-A"}
