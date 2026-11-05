"""
Project visibility and permission decisions — single source of truth.

* §15.3.3 project visibility: a non-administrator only sees projects whose
  task force they belong to (active membership) or lead.
* §15.2.4 / D5 data permissions: decided by the ``Role.permissions`` matrix.
  Inside a project, ``TaskForceMembership.role_in_project`` overrides the
  user's system role (§15.3.1). Administrators (and Django superusers)
  bypass the matrix — the only role-identity branch allowed by D5.
"""

from __future__ import annotations

from typing import Optional

from .models import ProjectTaskForce, Role, TaskForceMembership


def is_administrator(user) -> bool:
    """True if the user is a Django superuser or has an Administrator-level role."""
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    role = getattr(user, "role", None)
    return bool(role and getattr(role, "level", 0) >= Role.Level.ADMINISTRATOR)


def user_accessible_project_ids(user) -> Optional[list[int]]:
    """Project ids the user may see / operate on.

    Returns ``None`` for administrators (all projects), otherwise the sorted
    list of ``project_id`` from active memberships ∪ led task forces.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return []
    if is_administrator(user):
        return None

    member_ids = set(
        TaskForceMembership.objects.filter(
            user=user,
            is_active=True,
            task_force__is_active=True,
            task_force__project_id__isnull=False,
        ).values_list("task_force__project_id", flat=True)
    )
    leader_ids = set(
        ProjectTaskForce.objects.filter(
            leader=user, is_active=True, project_id__isnull=False
        ).values_list("project_id", flat=True)
    )
    return sorted(member_ids | leader_ids)


def user_can_access_project(user, project_id: int) -> bool:
    accessible = user_accessible_project_ids(user)
    if accessible is None:
        return True
    return int(project_id) in accessible


def effective_role(user, project_id: int | None = None):
    """System role, overridden by ``role_in_project`` inside a project."""
    if not user or not getattr(user, "is_authenticated", False):
        return None
    if project_id:
        membership = (
            TaskForceMembership.objects.filter(
                user=user,
                is_active=True,
                task_force__project_id=project_id,
                task_force__is_active=True,
                role_in_project__isnull=False,
            )
            .select_related("role_in_project")
            .first()
        )
        if membership is not None:
            return membership.role_in_project
    return getattr(user, "role", None)


def role_allows(role, resource: str, action: str) -> bool:
    if role is None:
        return False
    if role.level >= Role.Level.ADMINISTRATOR:
        return True
    matrix = role.permissions or {}
    return action in matrix.get(resource, []) or action in matrix.get("*", [])


def user_has_permission(
    user, resource: str, action: str, project_id: int | None = None
) -> bool:
    """Matrix check for ``resource``/``action`` (create|read|update|delete)."""
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if is_administrator(user):
        return True
    return role_allows(effective_role(user, project_id), resource, action)


def effective_permissions(user, project_id: int | None = None) -> dict:
    """The matrix the frontend uses to show/hide actions."""
    if is_administrator(user):
        from .rbac import build_permissions

        return build_permissions("ADMIN")
    role = effective_role(user, project_id)
    return dict(role.permissions or {}) if role else {}
