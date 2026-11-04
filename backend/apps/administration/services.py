"""
Administration services (§15.2 RBAC, §15.3 task forces, §15.7).
"""

from __future__ import annotations

from django.db import transaction
from django_tenants.utils import get_public_schema_name
from rest_framework import exceptions

from apps.core.exceptions import ServiceError
from apps.core.services import CrudService

from . import rbac
from .access import is_administrator
from .models import Organization, ProjectTaskForce, Role, TaskForceMembership, User


def project_exists(project_id) -> bool:
    from apps.tenants.models import ProjectTenant

    return (
        ProjectTenant.objects.filter(pk=project_id)
        .exclude(schema_name=get_public_schema_name())
        .exists()
    )


class OrganizationService(CrudService):
    model = Organization
    error_prefix = "ADM"

    def after_save(self, instance, *, creating, data):
        if creating:
            # Every organization gets the 7 system roles (§15.2.2, D5).
            rbac.ensure_system_roles(instance, Role)


class RoleService(CrudService):
    model = Role
    error_prefix = "ADM"

    def before_save(self, instance, *, creating, data):
        if not creating and instance.is_system_role and "code" in data:
            original = Role.objects.get(pk=instance.pk)
            if original.code != instance.code:
                raise ServiceError(
                    "The code of a system role cannot be changed.",
                    code="ADM_SYSTEM_ROLE_PROTECTED",
                    field="code",
                )

    def before_delete(self, instance):
        if instance.is_system_role:
            raise ServiceError(
                "System roles cannot be deleted.", code="ADM_SYSTEM_ROLE_PROTECTED"
            )


class UserService(CrudService):
    model = User
    error_prefix = "ADM"

    def create(self, data, *, batch_id=None):
        data = dict(data)
        password = data.pop("password", None)
        data.pop("password_confirm", None)
        if not data.get("role"):
            raise ServiceError(
                "Every user must have a system role (§15.2.3).",
                code="ADM_USER_ROLE_REQUIRED",
                field="role",
            )
        self._password = password
        return super().create(data, batch_id=batch_id)

    def before_save(self, instance, *, creating, data):
        if creating:
            if getattr(self, "_password", None):
                instance.set_password(self._password)
            else:
                instance.set_unusable_password()

    def update(self, instance, data, **kwargs):
        if "role" in data and not data["role"]:
            raise ServiceError(
                "Every user must have a system role (§15.2.3).",
                code="ADM_USER_ROLE_REQUIRED",
                field="role",
            )
        return super().update(instance, data, require_version=False, **kwargs)

    def set_password(self, instance, password: str):
        with transaction.atomic():
            instance.set_password(password)
            instance.save(update_fields=["password"])
            self._audit(
                "UPDATE",
                instance,
                old={"password": "***"},
                new={"password": "*** (reset)"},
            )


def _creator_role(user) -> str:
    if is_administrator(user):
        return ProjectTaskForce.CreatorRole.ADMINISTRATOR
    role = getattr(user, "role", None)
    # Recorded metadata only (not an authorization branch, D5).
    if role is not None and role.code == "PROJ_MGR":
        return ProjectTaskForce.CreatorRole.PROJECT_MANAGER
    return ProjectTaskForce.CreatorRole.PROJECT_ENGINEER


class TaskForceService(CrudService):
    """ADM-TF01 creation / management rules."""

    model = ProjectTaskForce
    error_prefix = "ADM"

    def _require_existing_project(self, project_id):
        if project_id in (None, ""):
            return
        if not project_exists(project_id):
            raise ServiceError(
                "Project does not exist.",
                code="ADM_PROJECT_NOT_FOUND",
                field="project_id",
            )

    def create(self, data, *, batch_id=None):
        data = dict(data)
        admin = is_administrator(self.user)
        if not admin:
            if not data.get("project_id"):
                raise ServiceError(
                    "Project Engineers must create a task force from an existing "
                    "project (ADM-TF01).",
                    code="ADM_TASK_FORCE_PROJECT_REQUIRED",
                    field="project_id",
                )
            # Non-administrators lead the group they create.
            data["leader"] = self.user
        self._require_existing_project(data.get("project_id"))
        data["created_by"] = self.user
        data["created_by_role"] = _creator_role(self.user)
        return super().create(data, batch_id=batch_id)

    def update(self, instance, data, **kwargs):
        data = dict(data)
        if not is_administrator(self.user):
            if "project_id" in data and data["project_id"] != instance.project_id:
                raise ServiceError(
                    "Only administrators can change the project of a task force.",
                    code="ADM_TASK_FORCE_PROJECT_LOCKED",
                    field="project_id",
                    status_code=403,
                )
            if "leader" in data and data["leader"] != instance.leader:
                raise ServiceError(
                    "Only administrators can change the task force leader.",
                    code="ADM_TASK_FORCE_LEADER_LOCKED",
                    field="leader",
                    status_code=403,
                )
        self._require_existing_project(data.get("project_id"))
        return super().update(instance, data, require_version=False, **kwargs)

    def assign_project(self, instance, project_id):
        if not is_administrator(self.user):
            raise exceptions.PermissionDenied()
        self._require_existing_project(project_id)
        return super().update(
            instance, {"project_id": project_id}, require_version=False
        )


class MembershipService(CrudService):
    model = TaskForceMembership
    error_prefix = "ADM"

    def add(self, task_force, user, role_in_project=None):
        if TaskForceMembership.objects.filter(
            task_force=task_force, user=user
        ).exists():
            raise ServiceError(
                "User is already a member of this task force.",
                code="ADM_MEMBER_DUPLICATE",
                field="user_id",
            )
        return self.create(
            {
                "task_force": task_force,
                "user": user,
                "role_in_project": role_in_project,
                "added_by": self.user,
            }
        )

    def remove(self, task_force, user_id):
        membership = TaskForceMembership.objects.filter(
            task_force=task_force, user_id=user_id
        ).first()
        if membership is None:
            raise exceptions.NotFound("Membership not found.")
        self.delete(membership)
