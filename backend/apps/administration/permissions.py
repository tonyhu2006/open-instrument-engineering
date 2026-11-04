"""
DRF permission classes.

* ``IsProjectMemberOrPublicSchema`` — §15.3.3 project visibility at the DRF
  layer (JWT authentication only happens inside DRF, so the middleware cannot
  see JWT users).
* ``RoleMatrixPermission`` — §15.2.4 data-permission matrix (decision D5):
  the view declares ``rbac_resource``; the HTTP method (or
  ``rbac_action_map[view.action]``) gives the action.
"""

from django_tenants.utils import get_public_schema_name
from rest_framework.permissions import BasePermission

from .access import (
    is_administrator,
    user_accessible_project_ids,
    user_has_permission,
)

METHOD_ACTIONS = {
    "GET": "read",
    "HEAD": "read",
    "OPTIONS": "read",
    "POST": "create",
    "PUT": "update",
    "PATCH": "update",
    "DELETE": "delete",
}


def current_project_id(request):
    tenant = getattr(request, "tenant", None)
    schema = getattr(tenant, "schema_name", None)
    if not schema or schema == get_public_schema_name():
        return None
    return getattr(tenant, "pk", None)


class IsProjectMemberOrPublicSchema(BasePermission):
    """Only administrators or task-force members may act inside a project."""

    message = "You are not a member of this project."

    def has_permission(self, request, view):
        project_id = current_project_id(request)
        if project_id is None:
            return True
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        accessible = user_accessible_project_ids(user)
        return accessible is None or project_id in accessible


class RoleMatrixPermission(BasePermission):
    """Checks ``Role.permissions[view.rbac_resource]`` for the request action."""

    message = "Your role does not allow this action."

    @staticmethod
    def action_for(request, view) -> str:
        action_map = getattr(view, "rbac_action_map", {}) or {}
        view_action = getattr(view, "action", None)
        if view_action in action_map:
            return action_map[view_action]
        return METHOD_ACTIONS.get(request.method, "update")

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        resource = getattr(view, "rbac_resource", None)
        if resource is None:
            return is_administrator(user)
        action = self.action_for(request, view)
        project_id = current_project_id(request)
        if user_has_permission(user, resource, action, project_id=project_id):
            return True
        # Read access granted through another permission (e.g. user/role
        # pickers needed to manage one's own task force, ADM-TF03).
        if action == "read":
            for other_resource, other_action in getattr(
                view, "rbac_read_delegates", ()
            ):
                if user_has_permission(
                    user, other_resource, other_action, project_id=project_id
                ):
                    return True
        return False


class IsAdministrator(BasePermission):
    """Administrator (level 5) or Django superuser."""

    message = "Only administrators can perform this action."

    def has_permission(self, request, view):
        return is_administrator(getattr(request, "user", None))


class TaskForceObjectPermission(BasePermission):
    """ADM-TF01: Administrators manage any task force; other creators (PM/PE
    with ``task_force.create``) manage only the groups they created."""

    message = "You can only manage task forces you created."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        if is_administrator(user):
            return True
        return obj.created_by_id == user.pk and user_has_permission(
            user, "task_force", "create"
        )
