"""
Seed RBAC roles per the design specification matrix.

Creates 7 system roles per organization:
  Level 5 — Administrator
  Level 4 — Project Manager   (display first within Level 4)
  Level 4 — Project Engineer
  Level 3 — Instrumentation Engineer
  Level 3 — Process Engineer
  Level 3 — Mechanical Engineer
  Level 1 — Guest

Permission matrix (from SPECIFICATION.md / design screenshot):

| Resource              | Admin | ProjEng | InstEng | ProcEng | MechEng | Guest |
|-----------------------|-------|---------|---------|---------|---------|-------|
| tag/loop/wiring       | CRUD  | CRUD    | CRUD    | R       | R       | R     |
| process_data          | CRUD  | CRUD    | R       | CRUD    | R       | R     |
| pipe_spec/connection  | CRUD  | CRUD    | R       | R       | CRUD    | R     |
| user/role/organization| CRUD  | —       | —       | —       | —       | —     |
| task_force            | CRUD  | CR*     | —       | —       | —       | —     |
| audit_log             | R     | —       | —       | —       | —       | —     |

Idempotent: re-running the command updates permission matrices but never
duplicates roles.

Usage:
    python manage.py seed_rbac
    python manage.py seed_rbac --org DEMO       # only specific org
    python manage.py seed_rbac --create-org     # create default DEMO org if missing
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.administration.models import Organization, Role

CRUD = ["create", "read", "update", "delete"]
R = ["read"]
CR = ["create", "read"]


def _permissions_for(level: int, code: str) -> dict:
    """Return permission matrix for the given role level/code."""

    # Administrator — wildcard full access
    if code == "ADMIN":
        return {
            "*": CRUD,
            "tag": CRUD,
            "loop": CRUD,
            "wiring": CRUD,
            "process_data": CRUD,
            "pipe_spec": CRUD,
            "connection": CRUD,
            "user": CRUD,
            "role": CRUD,
            "organization": CRUD,
            "task_force": CRUD,
            "audit_log": R,
        }

    # Project Manager / Project Engineer — full project access, can create task forces
    if code in ("PROJ_ENG", "PROJ_MGR"):
        return {
            "tag": CRUD,
            "loop": CRUD,
            "wiring": CRUD,
            "process_data": CRUD,
            "pipe_spec": CRUD,
            "connection": CRUD,
            # CR* on task force — create + read; update/delete only on own
            # (enforced at API)
            "task_force": CR,
        }

    # Instrumentation Engineer — Tag/Loop/Wiring CRUD; others read
    if code == "INST_ENG":
        return {
            "tag": CRUD,
            "loop": CRUD,
            "wiring": CRUD,
            "process_data": R,
            "pipe_spec": R,
            "connection": R,
        }

    # Process Engineer — ProcessData CRUD; others read
    if code == "PROC_ENG":
        return {
            "tag": R,
            "loop": R,
            "wiring": R,
            "process_data": CRUD,
            "pipe_spec": R,
            "connection": R,
        }

    # Mechanical Engineer — PipeSpec/Connection CRUD; others read
    if code == "MECH_ENG":
        return {
            "tag": R,
            "loop": R,
            "wiring": R,
            "process_data": R,
            "pipe_spec": CRUD,
            "connection": CRUD,
        }

    # Guest — read-only on engineering data
    if code == "GUEST":
        return {
            "tag": R,
            "loop": R,
            "wiring": R,
            "process_data": R,
            "pipe_spec": R,
            "connection": R,
        }

    return {}


ROLE_DEFINITIONS = [
    {
        "code": "ADMIN",
        "name": "Administrator",
        "level": Role.Level.ADMINISTRATOR,
        "description": "系统最高权限，可管理用户、角色、组织和所有项目数据",
        "display_order": 10,
    },
    {
        "code": "PROJ_MGR",
        "name": "Project Manager",
        "level": Role.Level.PROJECT_ENGINEER,
        "description": (
            "项目经理 — 负责项目总体进度、资源与商务协调；"
            "拥有项目内全专业读写权限，可创建并管理本人创建的工程项目组"
        ),
        "display_order": 20,
    },
    {
        "code": "PROJ_ENG",
        "name": "Project Engineer",
        "level": Role.Level.PROJECT_ENGINEER,
        "description": (
            "项目工程师 — 拥有项目内全专业读写权限；"
            "可基于项目号创建并管理本人创建的工程项目组"
        ),
        "display_order": 30,
    },
    {
        "code": "INST_ENG",
        "name": "Instrumentation Engineer",
        "level": Role.Level.ENGINEER_L3,
        "description": "仪表工程师 — 仪表/回路/接线 CRUD；其他模块只读",
        "display_order": 40,
    },
    {
        "code": "PROC_ENG",
        "name": "Process Engineer",
        "level": Role.Level.ENGINEER_L3,
        "description": "工艺工程师 — 工艺数据 CRUD；其他模块只读",
        "display_order": 50,
    },
    {
        "code": "MECH_ENG",
        "name": "Mechanical Engineer",
        "level": Role.Level.ENGINEER_L3,
        "description": "机械/管道工程师 — 管道规格/连接 CRUD；其他模块只读",
        "display_order": 60,
    },
    {
        "code": "GUEST",
        "name": "Guest",
        "level": Role.Level.GUEST,
        "description": "访客 — 所有工程数据只读",
        "display_order": 70,
    },
]


class Command(BaseCommand):
    help = (
        "Seed the 7 RBAC system roles per organization with the design "
        "permission matrix."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--org",
            type=str,
            default=None,
            help="Restrict seeding to a single organization code (e.g. 'DEMO').",
        )
        parser.add_argument(
            "--create-org",
            action="store_true",
            help="Create a default 'DEMO' organization if no organizations exist.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        org_code = options.get("org")
        create_org = options.get("create_org", False)

        if org_code:
            orgs = Organization.objects.filter(code=org_code)
            if not orgs.exists():
                self.stderr.write(
                    self.style.ERROR(f"Organization '{org_code}' not found.")
                )
                return
        else:
            orgs = Organization.objects.all()

        if not orgs.exists():
            if create_org:
                org = Organization.objects.create(
                    code="DEMO",
                    name="Demo Engineering Company",
                    description="Default organization (auto-created by seed_rbac)",
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created default organization: {org}")
                )
                orgs = Organization.objects.filter(pk=org.pk)
            else:
                self.stderr.write(
                    self.style.WARNING(
                        "No organizations exist. Re-run with --create-org to "
                        "create a default DEMO org, or create an organization "
                        "first via the admin UI."
                    )
                )
                return

        total_created = 0
        total_updated = 0

        for org in orgs:
            self.stdout.write(self.style.MIGRATE_HEADING(f"\n[{org.code}] {org.name}"))
            for definition in ROLE_DEFINITIONS:
                code = definition["code"]
                permissions = _permissions_for(definition["level"], code)
                defaults = {
                    "name": definition["name"],
                    "level": definition["level"],
                    "description": definition["description"],
                    "permissions": permissions,
                    "is_system_role": True,
                    "display_order": definition["display_order"],
                }

                role, created = Role.objects.get_or_create(
                    organization=org,
                    code=code,
                    defaults=defaults,
                )

                if created:
                    total_created += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  + {code:10s} L{role.level} — {role.name}"
                        )
                    )
                else:
                    # Refresh permission matrix and metadata to keep DB in sync
                    # with code
                    changed = False
                    for field, value in defaults.items():
                        if getattr(role, field) != value:
                            setattr(role, field, value)
                            changed = True
                    if changed:
                        role.save()
                        total_updated += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ~ {code:10s} L{role.level} — updated"
                            )
                        )
                    else:
                        self.stdout.write(f"  = {code:10s} L{role.level} — unchanged")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nRBAC seed complete: {total_created} created, "
                f"{total_updated} updated, across {orgs.count()} organization(s)."
            )
        )
