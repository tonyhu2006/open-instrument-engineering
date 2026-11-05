"""
Public-schema demo data — SPECIFICATION §4.8.1 (administration part).

Creates (idempotent):
* Organization ``DEMO`` with the 7 system roles (§15.2.2);
* one demo user per role (admin/admin123, others demo123);
* ProjectTenant ``PRJ-DEMO-001`` (schema ``project_prjdemo001``, Active);
* TaskForce ``TF-DEMO`` linked to it, with every demo user as member.

Run ``seed_demo_data`` afterwards for the tenant-schema engineering data.
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.administration.models import (
    Organization,
    ProjectTaskForce,
    Role,
    TaskForceMembership,
)
from apps.administration.rbac import ensure_system_roles
from apps.tenants import hierarchy_config
from apps.tenants.models import ProjectTenant

User = get_user_model()

DEMO_PROJECT_NO = "PRJ-DEMO-001"

DEMO_USERS = [
    # username, role code, first name, last name
    ("admin", "ADMIN", "System", "Administrator"),
    ("proj_manager", "PROJ_MGR", "Paula", "Manager"),
    ("proj_engineer", "PROJ_ENG", "Peter", "Engineer"),
    ("inst_engineer", "INST_ENG", "Irene", "Instrument"),
    ("proc_engineer", "PROC_ENG", "Paul", "Process"),
    ("mech_engineer", "MECH_ENG", "Mia", "Mechanical"),
    ("guest", "GUEST", "Gary", "Guest"),
]


class Command(BaseCommand):
    help = "Seed public-schema demo data (§4.8.1)."

    def handle(self, *args, **options):
        with transaction.atomic():
            org, _ = Organization.objects.get_or_create(
                code="DEMO",
                defaults={
                    "name": "Demo Engineering Company",
                    "description": "Demo organization for testing",
                },
            )
            ensure_system_roles(org, Role)
            self.stdout.write(f"Organization {org.code}: 7 system roles ready")

            users = []
            for username, role_code, first, last in DEMO_USERS:
                role = Role.objects.get(organization=org, code=role_code)
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "email": f"{username}@demo.openinstrument.local",
                        "first_name": first,
                        "last_name": last,
                        "organization": org,
                        "role": role,
                        "is_staff": role_code == "ADMIN",
                        "is_superuser": role_code == "ADMIN",
                    },
                )
                if created:
                    user.set_password("admin123" if role_code == "ADMIN" else "demo123")
                    user.save()
                elif user.role_id is None:
                    user.role = role
                    user.save(update_fields=["role"])
                users.append(user)
            self.stdout.write(f"Users: {', '.join(u.username for u in users)}")

        # Creating a tenant runs CREATE SCHEMA + tenant migrations; keep it
        # outside the transaction above.
        project = ProjectTenant.objects.filter(project_no=DEMO_PROJECT_NO).first()
        if project is None:
            project = ProjectTenant(
                project_no=DEMO_PROJECT_NO,
                name="Demo Project",
                organization_id=org.id,
                status=ProjectTenant.Status.ACTIVE,
                description="Minimal seed project (§4.8.1)",
                # The demo hierarchy is created by seed_demo_data.
                hierarchy_config=hierarchy_config.normalize(
                    {"template": "standard", "auto_create_defaults": False},
                    for_new_project=True,
                ),
            )
            project.save(verbosity=0)
        self.stdout.write(
            f"Project {project.project_no} → schema {project.schema_name}"
        )

        with transaction.atomic():
            admin = users[0]
            task_force, _ = ProjectTaskForce.objects.get_or_create(
                code="TF-DEMO",
                defaults={
                    "name": "Demo Task Force",
                    "project_id": project.pk,
                    "leader": admin,
                    "created_by": admin,
                    "created_by_role": ProjectTaskForce.CreatorRole.ADMINISTRATOR,
                },
            )
            for user in users:
                TaskForceMembership.objects.get_or_create(
                    task_force=task_force, user=user, defaults={"added_by": admin}
                )
        self.stdout.write(
            self.style.SUCCESS(
                f"TaskForce {task_force.code}: {task_force.memberships.count()} members"
            )
        )
