"""
RBAC definitions — SPECIFICATION §15.2.1 / §15.2.2 / §15.2.4 / decision D5.

Pure data (no model imports) so it can be used from data migrations.

* 5 permission levels (``Role.Level``), 7 system roles.
* Authorization is decided by the ``Role.permissions`` matrix
  ``{resource: [actions]}``; business code must never branch on
  ``role.code`` (Administrator bypass excepted).

Resource keys follow the §15.2.4 data-permission matrix. Three keys are not
rows of that table but are needed by implemented endpoints and are mapped to
the closest row (see docs/OPEN_QUESTIONS.md OQ-007):

* ``instrument_type``   → same as "Tag" (IDX-03 instrument types)
* ``naming_convention`` → same as "Plant Hierarchy" (project configuration)
* ``organization``      → read for everybody, CRUD Administrator
"""

CREATE, READ, UPDATE, DELETE = "create", "read", "update", "delete"
CRUD = [CREATE, READ, UPDATE, DELETE]
R = [READ]
CR = [CREATE, READ]
RU = [READ, UPDATE]

ACTIONS = tuple(CRUD)

# Resource groups (§15.2.4 rows)
ADMIN_ONLY = ["user", "role", "system_config"]
INSTRUMENTATION = [
    "tag",
    "loop",
    "specification",
    "wiring",
    "loop_drawing",
    "cable",
    "instrument_type",
]
PROCESS = ["process_data"]
MECHANICAL = ["pipe_specification", "process_connection"]
PROJECT_CONFIG = ["plant_hierarchy", "naming_convention"]

RESOURCES = (
    ADMIN_ONLY
    + ["task_force", "project", "audit_log", "organization"]
    + PROJECT_CONFIG
    + INSTRUMENTATION
    + PROCESS
    + MECHANICAL
)


def _grant(resources, actions):
    return {resource: list(actions) for resource in resources}


def _engineering(*, instrumentation, process, mechanical):
    perms = {}
    perms.update(_grant(INSTRUMENTATION, instrumentation))
    perms.update(_grant(PROCESS, process))
    perms.update(_grant(MECHANICAL, mechanical))
    return perms


def build_permissions(code: str) -> dict:
    """Permission matrix for a system role code (§15.2.4)."""
    if code == "ADMIN":
        perms = {"*": list(CRUD)}
        perms.update(_grant(RESOURCES, CRUD))
        perms["audit_log"] = list(R)
        return perms

    common_read = {"organization": list(R)}

    if code in ("PROJ_MGR", "PROJ_ENG"):
        perms = dict(common_read)
        perms.update(
            {"task_force": list(CR), "project": list(RU)},
        )
        perms.update(_grant(PROJECT_CONFIG, CRUD))
        perms.update(_engineering(instrumentation=CRUD, process=CRUD, mechanical=CRUD))
        return perms

    discipline = {
        "INST_ENG": dict(instrumentation=CRUD, process=R, mechanical=R),
        "PROC_ENG": dict(instrumentation=R, process=CRUD, mechanical=R),
        "MECH_ENG": dict(instrumentation=R, process=R, mechanical=CRUD),
        "GUEST": dict(instrumentation=R, process=R, mechanical=R),
    }
    if code in discipline:
        perms = dict(common_read)
        perms["project"] = list(R)
        perms.update(_grant(PROJECT_CONFIG, R))
        perms.update(_engineering(**discipline[code]))
        return perms
    return {}


# §15.2.2 preset roles (display order)
ROLE_DEFINITIONS = [
    {
        "code": "ADMIN",
        "name": "Administrator",
        "level": 5,
        "display_order": 10,
        "description": (
            "System administrator: manages users, roles, permissions, all task "
            "forces and projects; reads all audit logs."
        ),
    },
    {
        "code": "PROJ_MGR",
        "name": "Project Manager",
        "level": 4,
        "display_order": 20,
        "description": (
            "Project-level authority (business/schedule/resources); same "
            "permissions as Project Engineer."
        ),
    },
    {
        "code": "PROJ_ENG",
        "name": "Project Engineer",
        "level": 4,
        "display_order": 30,
        "description": (
            "Project-level authority (technical execution): CRUD on all "
            "disciplines, creates task forces for existing projects."
        ),
    },
    {
        "code": "INST_ENG",
        "name": "Instrumentation Engineer",
        "level": 3,
        "display_order": 40,
        "description": (
            "CRUD on instrumentation data (Tag/Loop/Specification/Wiring/"
            "LoopDrawing/Cable); read-only on other disciplines."
        ),
    },
    {
        "code": "PROC_ENG",
        "name": "Process Engineer",
        "level": 3,
        "display_order": 50,
        "description": "CRUD on process data; read-only on other disciplines.",
    },
    {
        "code": "MECH_ENG",
        "name": "Mechanical Engineer",
        "level": 3,
        "display_order": 60,
        "description": (
            "CRUD on piping data (PipeSpecification/ProcessConnection); "
            "read-only on other disciplines."
        ),
    },
    {
        "code": "GUEST",
        "name": "Guest",
        "level": 1,
        "display_order": 70,
        "description": "Read-only access to all data; can view and export.",
    },
]

SYSTEM_ROLE_CODES = tuple(r["code"] for r in ROLE_DEFINITIONS)


def ensure_system_roles(organization, role_model) -> list:
    """Create/refresh the 7 system roles of an organization (idempotent).

    ``role_model`` is passed in so data migrations can use the historical
    model. Existing system roles get their level, order and matrix refreshed.
    """
    roles = []
    for definition in ROLE_DEFINITIONS:
        role, _ = role_model.objects.update_or_create(
            organization=organization,
            code=definition["code"],
            defaults={
                "name": definition["name"],
                "level": definition["level"],
                "display_order": definition["display_order"],
                "description": definition["description"],
                "permissions": build_permissions(definition["code"]),
                "is_system_role": True,
            },
        )
        roles.append(role)
    return roles
