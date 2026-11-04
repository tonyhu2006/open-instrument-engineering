"""
RBAC Permission Classes

Implements role-based access control matching the permission matrix:

| Data Type            | Admin | ProjEng   | InstEng | ProcEng | MechEng | Guest |
|----------------------|-------|-----------|---------|---------|---------|-------|
| Tag/Loop/Wiring      | CRUD  | CRUD      | CRUD    | R       | R       | R     |
| ProcessData          | CRUD  | CRUD      | R       | CRUD    | R       | R     |
| PipeSpec/Connection  | CRUD  | CRUD      | R       | R       | CRUD    | R     |
| User/Role mgmt       | CRUD  | -         | -       | -       | -       | -     |
| Project Task Force   | CRUD  | CR* (own) | -       | -       | -       | -     |

Role hierarchy (level):
  5 = Administrator
  4 = Project Manager
  3 = Engineer (Instr/Proc/Mech) — code prefix discriminates discipline
  2 = Engineer Level 2
  1 = Guest
"""

from django_tenants.utils import get_public_schema_name
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Role


class IsProjectMemberOrPublicSchema(BasePermission):
    """
    Enforces SPECIFICATION.md §3.1.0.5.6 project visibility rule at the DRF level.

    - Requests targeting the public schema (no X-Project-ID or admin-only
      prefixes) are always allowed (auth still required by other permissions).
    - Requests targeting a project-tenant schema require the authenticated
      user to be a member or leader of that project, **unless** the user has
      Administrator role or is a Django superuser.
    """

    message = "You are not a member of this project."

    def has_permission(self, request, view):
        tenant = getattr(request, "tenant", None)
        if tenant is None:
            return True
        schema = getattr(tenant, "schema_name", None)
        if schema is None or schema == get_public_schema_name():
            return True
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        # Lazy import avoids a circular dependency (access → models → …).
        from .access import user_accessible_project_ids

        accessible = user_accessible_project_ids(user)
        if accessible is None:
            return True  # admin bypass
        pk = getattr(tenant, "pk", None)
        return pk is not None and pk in accessible


def _user_role_level(user) -> int:
    """Return numeric role level for a user, or 0 if no role/anonymous."""
    if not user or not user.is_authenticated:
        return 0
    # Django superuser bypass — full admin access
    if getattr(user, "is_superuser", False):
        return Role.Level.ADMINISTRATOR
    role = getattr(user, "role", None)
    if not role:
        return 0
    return role.level or 0


def _user_role_code(user) -> str:
    """Return uppercase role code for discipline checks (e.g. 'INST_ENG')."""
    if not user or not user.is_authenticated:
        return ""
    role = getattr(user, "role", None)
    if not role:
        return ""
    return (role.code or "").upper()


class IsAdministrator(BasePermission):
    """Only Administrator (level 5) can access. Django superuser also passes."""

    message = "Only administrators can perform this action."

    def has_permission(self, request, view):
        return _user_role_level(request.user) >= Role.Level.ADMINISTRATOR


class IsProjectEngineerOrAbove(BasePermission):
    """Project Manager (level 4) or Administrator (level 5)."""

    message = "Only project managers or administrators can perform this action."

    def has_permission(self, request, view):
        return _user_role_level(request.user) >= Role.Level.PROJECT_ENGINEER


class IsAuthenticatedReadOrAdminWrite(BasePermission):
    """
    Read: any authenticated user.
    Write: Administrator only.

    Use for resources like Organizations, Roles, Users, AuditLog.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return _user_role_level(request.user) >= Role.Level.ADMINISTRATOR


class TaskForcePermission(BasePermission):
    """
    Task Force creation and management rules:
    - Read: any authenticated user (visibility scope handled in queryset).
    - Create: Administrator OR Project Manager.
    - Update/Delete: Administrator (any) OR Project Manager (only own task forces).
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        # Write actions require PE+
        return _user_role_level(request.user) >= Role.Level.PROJECT_ENGINEER

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        level = _user_role_level(request.user)
        if level >= Role.Level.ADMINISTRATOR:
            return True
        if level >= Role.Level.PROJECT_ENGINEER:
            # PE can only modify task forces they lead/created
            leader_id = getattr(obj, "leader_id", None)
            return leader_id == request.user.id
        return False


class TaskForceMembershipPermission(BasePermission):
    """
    Task Force membership rules:
    - Administrator can manage any membership.
    - Project Manager can manage memberships of task forces they lead.
    - Others: read only.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return _user_role_level(request.user) >= Role.Level.PROJECT_ENGINEER

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        level = _user_role_level(request.user)
        if level >= Role.Level.ADMINISTRATOR:
            return True
        if level >= Role.Level.PROJECT_ENGINEER:
            tf = getattr(obj, "task_force", None)
            if tf and getattr(tf, "leader_id", None) == request.user.id:
                return True
        return False


# =============================================================================
# Engineering data permissions — applied per discipline (Instrumentation /
# Process / Mechanical). Guest is read-only on everything.
# =============================================================================

# Conventional role codes used to identify discipline
INSTRUMENT_CODES = {"INST_ENG", "INSTRUMENTATION", "INSTRUMENT_ENGINEER", "INSTR_ENG"}
PROCESS_CODES = {"PROC_ENG", "PROCESS", "PROCESS_ENGINEER"}
MECHANICAL_CODES = {"MECH_ENG", "MECHANICAL", "MECHANICAL_ENGINEER", "PIPE_ENG"}


def _can_write_discipline(user, discipline_codes: set) -> bool:
    """Admin and PE can always write; specific discipline engineer can write."""
    level = _user_role_level(user)
    if level >= Role.Level.PROJECT_ENGINEER:
        return True
    if level >= Role.Level.ENGINEER_L3:
        return _user_role_code(user) in discipline_codes
    return False


class CanEditInstrumentation(BasePermission):
    """Tag/Loop/Wiring: Admin/PE/Instr Engr can write; everyone else read."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return _can_write_discipline(request.user, INSTRUMENT_CODES)


class CanEditProcess(BasePermission):
    """Process data: Admin/PE/Process Engr can write; everyone else read."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return _can_write_discipline(request.user, PROCESS_CODES)


class CanEditMechanical(BasePermission):
    """Pipe spec / connection: Admin/PE/Mech Engr can write."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return _can_write_discipline(request.user, MECHANICAL_CODES)
