"""
Project visibility / access control helpers.

Implements SPECIFICATION.md §3.1.0.5.6 "项目可见性规则":
A regular user can only see / operate on engineering projects (ProjectTenant)
they are a member OR leader of (via ProjectTaskForce). Administrators and
Django superusers bypass this restriction.

This module is the single source of truth for that rule. It must be consulted
by every code path that exposes project lists or validates X-Project-ID.
"""
from __future__ import annotations

from typing import Optional

from .models import ProjectTaskForce, Role, TaskForceMembership


def is_administrator(user) -> bool:
    """True if the user is a Django superuser or has Administrator role."""
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_superuser", False):
        return True
    role = getattr(user, "role", None)
    return bool(role and getattr(role, "level", 0) >= Role.Level.ADMINISTRATOR)


def user_accessible_project_ids(user) -> Optional[list[int]]:
    """
    Return the list of project_ids the user can see/operate on.

    Returns:
        None  — administrator / superuser: access ALL projects (bypass).
        []    — authenticated user without any TaskForce membership or leadership.
        [ids] — sorted list of project_ids from memberships ∪ leaderships.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return []
    if is_administrator(user):
        return None

    member_ids = set(
        TaskForceMembership.objects
        .filter(user=user)
        .values_list("task_force__project_id", flat=True)
    )
    leader_ids = set(
        ProjectTaskForce.objects
        .filter(leader=user)
        .values_list("project_id", flat=True)
    )
    return sorted(member_ids | leader_ids)


def user_can_access_project(user, project_id: int) -> bool:
    """Shorthand: is the user allowed to access the given project_id?"""
    accessible = user_accessible_project_ids(user)
    if accessible is None:
        return True
    return int(project_id) in accessible
