"""
Regression suite for the SPECIFICATION alignment of already-implemented
features (Module 15, Part 4 global contracts, decisions D1/D2/D5).

Each test names the spec clause it pins down.
"""

from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import schema_context
from rest_framework_simplejwt.tokens import RefreshToken

from apps.administration.models import ProjectTaskForce, TaskForceMembership
from apps.audit.models import AuditLog, AuditLogImmutableError
from apps.core_engineering.models import (
    Client,
    Loop,
    Plant,
    PlantHierarchy,
    Tag,
)
from apps.core_engineering.services import (
    InstrumentTypeService,
    PlantHierarchyService,
    PlantService,
    SiteService,
)
from apps.tenants.models import ProjectTenant

pytestmark = pytest.mark.django_db
User = get_user_model()
V1 = "/api/v1"


# =============================================================================
# helpers / fixtures
# =============================================================================


def call(client, method, url, user=None, project=None, data=None, **extra):
    headers = dict(extra)
    if user is not None:
        token = RefreshToken.for_user(user).access_token
        headers["HTTP_AUTHORIZATION"] = f"Bearer {token}"
    if project is not None:
        headers["HTTP_X_PROJECT_ID"] = str(project.pk)
    kwargs = {"content_type": "application/json"} if data is not None else {}
    return getattr(client, method)(url, data=data, **kwargs, **headers)


def rows(response):
    body = response.json()
    return body["results"] if isinstance(body, dict) and "results" in body else body


@pytest.fixture
def people(isolation_tenants, roles):
    """One user per system role; all but ``outsider`` are members of A."""
    org = isolation_tenants.org

    def make(username, code, member=True):
        user = User.objects.create_user(
            username=username,
            password="secret123",
            organization=org,
            role=roles[code],
            email=f"{username}@example.com",
        )
        if member:
            TaskForceMembership.objects.create(user=user, task_force=tf_a)
        return user

    admin = User.objects.create_user(
        username="c_admin", password="secret123", organization=org, role=roles["ADMIN"]
    )
    tf_a = ProjectTaskForce.objects.create(
        project_id=isolation_tenants.a.pk,
        code="TF-CONF-A",
        name="A",
        created_by=admin,
        created_by_role="ADMINISTRATOR",
    )
    return SimpleNamespace(
        admin=admin,
        pe=make("c_pe", "PROJ_ENG"),
        pm=make("c_pm", "PROJ_MGR"),
        inst=make("c_inst", "INST_ENG"),
        proc=make("c_proc", "PROC_ENG"),
        guest=make("c_guest", "GUEST"),
        outsider=make("c_out", "PROJ_ENG", member=False),
        tf_a=tf_a,
        roles=roles,
        a=isolation_tenants.a,
        b=isolation_tenants.b,
    )


@pytest.fixture
def hier(isolation_tenants):
    """Client → Site → Plant (root auto-created) → Area → U1/U2 in project A."""
    with schema_context(isolation_tenants.a.schema_name):
        client = Client.objects.get(code="SHARED")
        site = SiteService().create({"client": client, "code": "S1", "name": "S1"})
        plant = PlantService().create({"site": site, "code": "P1", "name": "P1"})
        root = PlantHierarchy.alive.get(plant=plant, parent__isnull=True)
        hs = PlantHierarchyService()
        area = hs.create(
            {"parent": root, "code": "A1", "name": "A1", "node_type": "AREA"}
        )
        area2 = hs.create(
            {"parent": root, "code": "A2", "name": "A2", "node_type": "AREA"}
        )
        u1 = hs.create(
            {"parent": area, "code": "U1", "name": "U1", "node_type": "UNIT"}
        )
        u2 = hs.create(
            {"parent": area, "code": "U2", "name": "U2", "node_type": "UNIT"}
        )
        ft = InstrumentTypeService().create(
            {"code": "FT", "name": "Flow transmitter", "category": "TRANSMITTER"}
        )
    connection.set_schema_to_public()
    return SimpleNamespace(
        client=client,
        site=site,
        plant=plant,
        root=root,
        area=area,
        area2=area2,
        u1=u1,
        u2=u2,
        ft=ft,
    )


# =============================================================================
# §15.2.4 / D5 — RBAC matrix enforcement
# =============================================================================


class TestRbacMatrix:
    def test_guest_member_can_read_but_not_write(self, client, people):
        url = f"{V1}/clients/"
        assert call(client, "get", url, people.guest, people.a).status_code == 200
        resp = call(
            client, "post", url, people.guest, people.a, {"code": "G", "name": "G"}
        )
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "AUTH_PERMISSION_DENIED"

    def test_discipline_rules(self, client, people, hier):
        payload = {
            "tag_number": "FT-100",
            "unit": hier.u1.pk,
            "instrument_type": hier.ft.pk,
        }
        url = f"{V1}/instruments/"
        assert (
            call(client, "post", url, people.proc, people.a, payload).status_code == 403
        )
        assert (
            call(client, "post", url, people.inst, people.a, payload).status_code == 201
        )

    def test_role_in_project_overrides_system_role(self, client, people):
        membership = TaskForceMembership.objects.get(user=people.guest)
        membership.role_in_project = people.roles["INST_ENG"]
        membership.save()
        resp = call(
            client,
            "post",
            f"{V1}/instrument-types/",
            people.guest,
            people.a,
            {"code": "PT", "name": "PT", "category": "TRANSMITTER"},
        )
        assert resp.status_code == 201

    def test_permission_matrix_is_schema_validated(self, client, people):
        role = people.roles["GUEST"]
        resp = call(
            client,
            "patch",
            f"{V1}/roles/{role.pk}/",
            people.admin,
            data={"permissions": {"nuclear_launch": ["create"]}},
        )
        assert resp.status_code == 400

    def test_system_roles_cannot_be_deleted(self, client, people):
        role = people.roles["GUEST"]
        resp = call(client, "delete", f"{V1}/roles/{role.pk}/", people.admin)
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "ADM_SYSTEM_ROLE_PROTECTED"


# =============================================================================
# §15.1.3 / §15.2.4 "Project" row / §15.4.6
# =============================================================================


class TestProjects:
    url = f"{V1}/tenants/projects/"

    def test_only_admin_creates_projects(self, client, people):
        for user in (people.guest, people.pe):
            resp = call(
                client, "post", self.url, user, data={"project_no": "X-1", "name": "x"}
            )
            assert resp.status_code == 403, user.username
        assert not ProjectTenant.objects.filter(project_no="X-1").exists()

    def test_admin_create_derives_schema_and_default_hierarchy(self, client, people):
        resp = call(
            client,
            "post",
            self.url,
            people.admin,
            data={"project_no": "PRJ-2099-001", "name": "New"},
        )
        assert resp.status_code == 201, resp.content
        body = resp.json()
        assert body["schema_name"] == "project_prj2099001"
        assert body["hierarchy_config"]["template"] == "standard"
        project = ProjectTenant.objects.get(pk=body["id"])
        with schema_context(project.schema_name):
            plant = Plant.alive.get()
            assert plant.name == "主装置"
            assert plant.site.client.name == "客户"
            assert PlantHierarchy.alive.get(plant=plant).node_type == "PLANT"
        assert AuditLog.objects.filter(
            model_name="ProjectTenant", object_id=str(project.pk), action="CREATE"
        ).exists()

    def test_invalid_hierarchy_config_rejected(self, client, people):
        resp = call(
            client,
            "post",
            self.url,
            people.admin,
            data={
                "project_no": "PRJ-BAD",
                "name": "x",
                "hierarchy_config": {"levels": [{"name": "Galaxy"}]},
            },
        )
        assert resp.status_code == 400

    def test_project_row_permissions(self, client, people):
        url = f"{self.url}{people.a.pk}/"
        patch = {"description": "edited"}
        assert call(client, "patch", url, people.guest, data=patch).status_code == 403
        assert call(client, "patch", url, people.pe, data=patch).status_code == 200
        assert call(client, "delete", url, people.pe).status_code == 403


# =============================================================================
# §15.3 task forces (ADM-TF01) and visibility (§15.3.3)
# =============================================================================


class TestTaskForces:
    url = f"{V1}/task-forces/"

    def test_pe_creates_one_group_per_existing_project(self, client, people):
        resp = call(
            client,
            "post",
            self.url,
            people.outsider,
            data={"project_id": people.b.pk, "code": "TF-B", "name": "B"},
        )
        assert resp.status_code == 201, resp.content
        body = resp.json()
        assert body["created_by_role"] == "PROJECT_ENGINEER"
        assert body["leader"] == people.outsider.pk
        again = call(
            client,
            "post",
            self.url,
            people.pe,
            data={"project_id": people.b.pk, "code": "TF-B2", "name": "B2"},
        )
        assert again.status_code == 400
        assert again.json()["error"]["code"] == "ADM_TASK_FORCE_PROJECT_TAKEN"

    def test_pe_needs_existing_project(self, client, people):
        for project_id in (None, 987654):
            resp = call(
                client,
                "post",
                self.url,
                people.pe,
                data={"project_id": project_id, "code": "TF-X", "name": "x"},
            )
            assert resp.status_code == 400

    def test_pe_cannot_touch_foreign_or_relink_own_group(self, client, people):
        # Admin-created group: PE may not edit it.
        resp = call(
            client,
            "patch",
            f"{self.url}{people.tf_a.pk}/",
            people.pe,
            data={"name": "hijack"},
        )
        assert resp.status_code == 403
        own = call(
            client,
            "post",
            self.url,
            people.outsider,
            data={"project_id": people.b.pk, "code": "TF-OWN", "name": "own"},
        ).json()
        resp = call(
            client,
            "patch",
            f"{self.url}{own['id']}/",
            people.outsider,
            data={"project_id": people.a.pk},
        )
        assert resp.status_code == 403

    def test_membership_escalation_closed(self, client, people):
        assert (
            call(
                client,
                "post",
                f"{V1}/task-force-memberships/",
                people.outsider,
                data={},
            ).status_code
            == 404
        )
        resp = call(
            client,
            "post",
            f"{self.url}{people.tf_a.pk}/members/",
            people.outsider,
            data={"user_id": people.outsider.pk},
        )
        assert resp.status_code in (403, 404)
        assert (
            call(client, "get", f"{V1}/clients/", people.outsider, people.a).status_code
            == 403
        )

    def test_admin_manages_members(self, client, people):
        url = f"{self.url}{people.tf_a.pk}/members/"
        resp = call(
            client,
            "post",
            url,
            people.admin,
            data={"user_id": people.outsider.pk, "role_in_project": None},
        )
        assert resp.status_code == 201
        assert resp.json()["added_by"] == people.admin.pk
        assert (
            call(client, "get", f"{V1}/clients/", people.outsider, people.a).status_code
            == 200
        )
        resp = call(client, "delete", f"{url}{people.outsider.pk}/", people.admin)
        assert resp.status_code == 204
        assert (
            call(client, "get", f"{V1}/clients/", people.outsider, people.a).status_code
            == 403
        )

    def test_inactive_membership_grants_nothing(self, client, people):
        TaskForceMembership.objects.filter(user=people.inst).update(is_active=False)
        assert (
            call(client, "get", f"{V1}/clients/", people.inst, people.a).status_code
            == 403
        )

    def test_assign_project_is_admin_only(self, client, people):
        empty = ProjectTaskForce.objects.create(code="TF-EMPTY", name="empty")
        url = f"{self.url}{empty.pk}/assign-project/"
        data = {"project_id": people.b.pk}
        assert call(client, "post", url, people.pe, data=data).status_code in (403, 404)
        resp = call(client, "post", url, people.admin, data=data)
        assert resp.status_code == 200
        assert resp.json()["project_id"] == people.b.pk


# =============================================================================
# §15.7 users / me
# =============================================================================


class TestUsersAndMe:
    def test_user_list_is_restricted(self, client, people):
        assert call(client, "get", f"{V1}/users/", people.guest).status_code == 403
        assert call(client, "get", f"{V1}/users/", people.pe).status_code == 200

    def test_user_requires_role_and_unique_email(self, client, people):
        base = {
            "username": "newbie",
            "password": "verysecret1",
            "password_confirm": "verysecret1",
            "email": "c_pe@example.com",
        }
        assert (
            call(client, "post", f"{V1}/users/", people.admin, data=base).status_code
            == 400
        )
        base["role"] = people.roles["GUEST"].pk
        resp = call(client, "post", f"{V1}/users/", people.admin, data=base)
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "ADM_USER_EMAIL_DUPLICATE"

    def test_reset_password(self, client, people):
        resp = call(
            client,
            "post",
            f"{V1}/users/{people.guest.pk}/reset-password/",
            people.admin,
            data={"password": "brandnew123", "password_confirm": "brandnew123"},
        )
        assert resp.status_code == 200
        people.guest.refresh_from_db()
        assert people.guest.check_password("brandnew123")

    def test_me_and_preferences(self, client, people):
        me = call(client, "get", f"{V1}/me/", people.guest).json()
        assert me["permissions"]["tag"] == ["read"]
        resp = call(
            client,
            "patch",
            f"{V1}/me/preferences/",
            people.guest,
            data={"tableWidths": {"t": {"a": 10}}, "language": "zh-CN"},
        )
        assert resp.status_code == 200
        assert resp.json()["language"] == "zh-CN"
        resp = call(
            client,
            "patch",
            f"{V1}/me/preferences/",
            people.guest,
            data={"language": "xx"},
        )
        assert resp.status_code == 400
        forces = call(client, "get", f"{V1}/me/task-forces/", people.guest).json()
        assert [f["code"] for f in forces] == ["TF-CONF-A"]


# =============================================================================
# §4.2 API contract, D1 auth alias
# =============================================================================


class TestApiContract:
    def test_tenant_endpoint_without_project_header(self, client, people):
        resp = call(client, "get", f"{V1}/clients/", people.admin)
        assert resp.status_code == 400
        err = resp.json()["error"]
        assert err["code"] == "AUTH_PROJECT_REQUIRED"
        assert set(err) == {"code", "message", "field", "details", "trace_id"}

    def test_page_size_parameter(self, client, people):
        resp = call(client, "get", f"{V1}/users/?page_size=2", people.admin)
        body = resp.json()
        assert len(body["results"]) == 2 and body["count"] > 2

    def test_auth_paths_and_deprecated_alias(self, client, people):
        creds = {"username": "c_guest", "password": "secret123"}
        new = client.post(f"{V1}/auth/login/", creds, content_type="application/json")
        assert new.status_code == 200 and "Deprecation" not in new
        old = client.post("/api/token/", creds, content_type="application/json")
        assert old.status_code == 200
        assert old["Deprecation"] == "true" and "Sunset" in old
        bad = client.post(
            f"{V1}/auth/login/",
            {"username": "c_guest", "password": "nope"},
            content_type="application/json",
        )
        assert bad.json()["error"]["code"] == "AUTH_INVALID_CREDENTIALS"

    def test_legacy_prefixes_are_gone(self, client, people):
        for url in ("/api/engineering/clients/", "/api/admin/users/"):
            assert call(client, "get", url, people.admin, people.a).status_code == 404


# =============================================================================
# §4.1 five essentials: validation, row_version, soft delete, audit
# =============================================================================


class TestWriteContract:
    def test_optimistic_lock(self, client, people, hier):
        url = f"{V1}/clients/{hier.client.pk}/"
        resp = call(client, "patch", url, people.pe, people.a, {"name": "x"})
        assert resp.json()["error"]["code"] == "ADM_ROW_VERSION_REQUIRED"
        resp = call(
            client,
            "patch",
            url,
            people.pe,
            people.a,
            {"name": "x", "expected_row_version": 99},
        )
        assert resp.status_code == 409
        assert resp.json()["error"]["details"]["current_row_version"] == 1
        resp = call(
            client,
            "patch",
            url,
            people.pe,
            people.a,
            {"name": "x", "expected_row_version": 1},
        )
        assert resp.status_code == 200
        assert resp.json()["row_version"] == 2
        assert resp.json()["updated_by_id"] == people.pe.pk

    def test_business_error_codes_and_per_unit_uniqueness(self, client, people, hier):
        url = f"{V1}/instruments/"
        tag = {"tag_number": "FT-1", "unit": hier.u1.pk, "instrument_type": hier.ft.pk}
        assert call(client, "post", url, people.inst, people.a, tag).status_code == 201
        resp = call(client, "post", url, people.inst, people.a, tag)
        assert resp.json()["error"]["code"] == "IDX_TAG_DUPLICATE"
        tag["unit"] = hier.u2.pk
        assert call(client, "post", url, people.inst, people.a, tag).status_code == 201
        loop = {"loop_tag": "F-1", "function": "F"}
        for unit in (hier.u1, hier.u2):
            resp = call(
                client,
                "post",
                f"{V1}/loops/",
                people.inst,
                people.a,
                {**loop, "unit": unit.pk},
            )
            assert resp.status_code == 201, "loop numbers are unique per unit (§4.1.6)"

    def test_loop_must_share_tag_unit(self, client, people, hier):
        loop = call(
            client,
            "post",
            f"{V1}/loops/",
            people.inst,
            people.a,
            {"loop_tag": "F-9", "function": "F", "unit": hier.u2.pk},
        ).json()
        resp = call(
            client,
            "post",
            f"{V1}/instruments/",
            people.inst,
            people.a,
            {
                "tag_number": "FT-9",
                "unit": hier.u1.pk,
                "instrument_type": hier.ft.pk,
                "loop": loop["id"],
            },
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["field"] == "loop"

    def test_soft_delete_cascade_and_protect(self, client, people, hier):
        with schema_context(people.a.schema_name):
            Tag.objects.create(tag_number="FT-7", unit=hier.u1, instrument_type=hier.ft)
        connection.set_schema_to_public()
        url = f"{V1}/plants/{hier.plant.pk}/"
        resp = call(client, "delete", url, people.pe, people.a)
        assert resp.status_code == 409
        assert resp.json()["error"]["details"]["referenced_by"] == {"Tag": 1}
        with schema_context(people.a.schema_name):
            Tag.objects.filter(tag_number="FT-7").update(is_deleted=True)
        connection.set_schema_to_public()
        assert call(client, "delete", url, people.pe, people.a).status_code == 204
        with schema_context(people.a.schema_name):
            assert Plant.objects.get(pk=hier.plant.pk).is_deleted
            assert not PlantHierarchy.alive.filter(plant=hier.plant).exists()
            # root P1 + areas A1/A2 + units U1/U2, all soft-deleted in place
            assert PlantHierarchy.objects.filter(plant=hier.plant).count() == 5
        batch = AuditLog.objects.filter(model_name="PlantHierarchy", action="DELETE")
        assert batch.count() == 5 and len(set(batch.values_list("batch_id"))) == 1
        # code is reusable after a soft delete
        resp = call(
            client,
            "post",
            f"{V1}/plants/",
            people.pe,
            people.a,
            {"site": hier.site.pk, "code": "P1", "name": "P1 again"},
        )
        assert resp.status_code == 201

    def test_audit_records_are_complete_and_immutable(self, client, people, hier):
        call(
            client,
            "patch",
            f"{V1}/clients/{hier.client.pk}/",
            people.pe,
            people.a,
            {"name": "Renamed", "expected_row_version": 1},
        )
        log = AuditLog.objects.get(model_name="Client", action="UPDATE")
        assert log.project_id == people.a.pk and log.user == people.pe
        assert "name" in log.changed_fields
        change = log.change_details["changes"][0]
        assert change["change_type"] == "modified"
        log.object_repr = "tampered"
        with pytest.raises(AuditLogImmutableError):
            log.save()
        with pytest.raises(AuditLogImmutableError):
            AuditLog.objects.all().delete()


# =============================================================================
# §15.4.5 plant hierarchy / §5.4.3 move & filters
# =============================================================================


class TestHierarchy:
    def test_plant_root_and_inheritance(self, hier, people):
        with schema_context(people.a.schema_name):
            assert hier.root.plant_id == hier.plant.pk
            assert PlantHierarchy.objects.get(pk=hier.u1.pk).plant_id == hier.plant.pk

    def test_move_and_type_rules(self, client, people, hier):
        url = f"{V1}/plant-hierarchy/{hier.u2.pk}/move/"
        resp = call(client, "post", url, people.pe, people.a, {"parent": hier.area2.pk})
        assert resp.status_code == 200 and resp.json()["parent"] == hier.area2.pk
        resp = call(client, "post", url, people.pe, people.a, {"parent": hier.root.pk})
        assert resp.status_code == 400

    def test_tree_view_and_tag_filters(self, client, people, hier):
        with schema_context(people.a.schema_name):
            Tag.objects.create(tag_number="FT-3", unit=hier.u1, instrument_type=hier.ft)
        connection.set_schema_to_public()
        tree = call(
            client, "get", f"{V1}/plant-hierarchy/?tree=true", people.guest, people.a
        ).json()
        assert tree[0]["children"][0]["code"] == "A1"
        for query in (
            f"plant={hier.plant.pk}",
            f"site={hier.site.pk}",
            f"client={hier.client.pk}",
            f"node={hier.area.pk}",
        ):
            got = rows(
                call(
                    client, "get", f"{V1}/instruments/?{query}", people.guest, people.a
                )
            )
            assert [t["tag_number"] for t in got] == ["FT-3"], query
        got = rows(
            call(
                client,
                "get",
                f"{V1}/instruments/?plant={hier.plant.pk + 999}",
                people.guest,
                people.a,
            )
        )
        assert got == []


# =============================================================================
# §15.5 naming conventions / IDX-01
# =============================================================================


class TestNaming:
    def _simple_default(self, client, people):
        resp = call(
            client,
            "post",
            f"{V1}/naming-conventions/from-template/",
            people.pe,
            people.a,
            {"template": "SIMPLE", "is_default": True},
        )
        assert resp.status_code == 201, resp.content
        return resp.json()

    def test_templates_listed(self, client, people):
        resp = call(
            client, "get", f"{V1}/naming-conventions/templates/", people.guest, people.a
        )
        assert {t["code"] for t in resp.json()} >= {
            "ISA_5_1",
            "FULL_HIERARCHY",
            "CABLE",
        }

    def test_invalid_regex_rejected(self, client, people):
        resp = call(
            client,
            "post",
            f"{V1}/naming-conventions/",
            people.pe,
            people.a,
            {"name": "bad", "pattern": "([", "entity_type": "TAG"},
        )
        assert resp.status_code == 400 and resp.json()["error"]["field"] == "pattern"

    def test_validate_parse_generate(self, client, people, hier):
        self._simple_default(client, people)
        ok = call(
            client,
            "post",
            f"{V1}/tags/validate-number/",
            people.guest,
            people.a,
            {
                "number": "FT-101",
                "unit_id": hier.u1.pk,
                "instrument_type_id": hier.ft.pk,
            },
        ).json()
        assert ok["valid"] and ok["segments"] == {"function": "FT", "sequence": "101"}
        bad = call(
            client,
            "post",
            f"{V1}/tags/validate-number/",
            people.guest,
            people.a,
            {"number": "FT101"},
        ).json()
        assert not bad["valid"]
        assert bad["errors"][0]["code"] == "IDX_INVALID_NAMING_SEGMENT"
        gen_url = f"{V1}/tags/generate-number/"
        gen = {"unit_id": hier.u1.pk, "instrument_type_id": hier.ft.pk}
        first = call(client, "post", gen_url, people.inst, people.a, gen).json()
        assert first["generated_number"] == "FT-001"
        call(
            client,
            "post",
            f"{V1}/instruments/",
            people.inst,
            people.a,
            {"tag_number": "FT-001", "unit": hier.u1.pk, "instrument_type": hier.ft.pk},
        )
        second = call(client, "post", gen_url, people.inst, people.a, gen).json()
        assert second["generated_number"] == "FT-002"

    def test_tag_creation_enforces_default_convention(self, client, people, hier):
        self._simple_default(client, people)
        url = f"{V1}/instruments/"
        base = {"unit": hier.u1.pk, "instrument_type": hier.ft.pk}
        resp = call(
            client, "post", url, people.inst, people.a, {**base, "tag_number": "ft_1"}
        )
        assert resp.json()["error"]["code"] == "IDX_INVALID_NAMING_SEGMENT"
        resp = call(
            client, "post", url, people.inst, people.a, {**base, "tag_number": "PT-101"}
        )
        assert resp.json()["error"]["code"] == "IDX_NAMING_FUNCTION_MISMATCH"

    def test_one_default_per_entity_type(self, client, people):
        first = self._simple_default(client, people)
        second = call(
            client,
            "post",
            f"{V1}/naming-conventions/from-template/",
            people.pe,
            people.a,
            {"template": "ISA_5_1", "name": "ISA", "is_default": True},
        ).json()
        with schema_context(people.a.schema_name):
            from apps.core_engineering.models import NamingConvention

            defaults = NamingConvention.alive.filter(is_default=True)
            assert list(defaults.values_list("pk", flat=True)) == [second["id"]]
            assert first["id"] != second["id"]
        assert Loop is not None  # keep import for readability of the module
