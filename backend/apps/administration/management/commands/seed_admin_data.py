"""
Management command to seed administration demo data.
Creates demo organization, project hierarchy, roles, and users.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.administration.models import (
    Organization,
    Project,
    Client,
    Site,
    Plant,
    Role,
    NamingConvention,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Seed administration demo data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding administration demo data...")
        
        # Create Organization
        org, created = Organization.objects.get_or_create(
            code="DEMO",
            defaults={
                "name": "Demo Engineering Company",
                "description": "Demo organization for testing",
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created organization: {org}"))
        else:
            self.stdout.write(f"Organization exists: {org}")
        
        # Create Roles
        roles_data = [
            {
                "code": "ADMIN",
                "name": "Administrator",
                "level": Role.Level.ADMINISTRATOR,
                "description": "System administrator with full access",
                "permissions": {"*": ["create", "read", "update", "delete"]},
                "is_system_role": True,
            },
            {
                "code": "PROJ_ENG",
                "name": "Project Engineer",
                "level": Role.Level.PROJECT_ENGINEER,
                "description": "Project engineer with full project access",
                "permissions": {
                    "tag": ["create", "read", "update", "delete"],
                    "loop": ["create", "read", "update", "delete"],
                    "specification": ["create", "read", "update", "delete"],
                },
                "is_system_role": True,
            },
            {
                "code": "INST_ENG",
                "name": "Instrumentation Engineer",
                "level": Role.Level.ENGINEER_L3,
                "description": "Instrumentation engineer",
                "permissions": {
                    "tag": ["create", "read", "update"],
                    "loop": ["create", "read", "update"],
                    "specification": ["create", "read", "update"],
                },
                "is_system_role": True,
            },
            {
                "code": "PROC_ENG",
                "name": "Process Engineer",
                "level": Role.Level.ENGINEER_L3,
                "description": "Process engineer",
                "permissions": {
                    "process_data": ["create", "read", "update"],
                    "tag": ["read"],
                    "specification": ["read"],
                },
                "is_system_role": True,
            },
            {
                "code": "GUEST",
                "name": "Guest",
                "level": Role.Level.GUEST,
                "description": "Read-only access",
                "permissions": {
                    "tag": ["read"],
                    "loop": ["read"],
                    "specification": ["read"],
                },
                "is_system_role": True,
            },
        ]
        
        roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                organization=org,
                code=role_data["code"],
                defaults=role_data
            )
            roles[role_data["code"]] = role
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created role: {role}"))
        
        # Create Admin User
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@demo.com",
                "first_name": "Admin",
                "last_name": "User",
                "organization": org,
                "role": roles["ADMIN"],
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"Created admin user: {admin_user}"))
        
        # Create Demo Users
        demo_users = [
            {
                "username": "proj_engineer",
                "email": "proj@demo.com",
                "first_name": "Project",
                "last_name": "Engineer",
                "role": roles["PROJ_ENG"],
            },
            {
                "username": "inst_engineer",
                "email": "inst@demo.com",
                "first_name": "Instrumentation",
                "last_name": "Engineer",
                "role": roles["INST_ENG"],
            },
            {
                "username": "proc_engineer",
                "email": "proc@demo.com",
                "first_name": "Process",
                "last_name": "Engineer",
                "role": roles["PROC_ENG"],
            },
        ]
        
        for user_data in demo_users:
            user, created = User.objects.get_or_create(
                username=user_data["username"],
                defaults={
                    **user_data,
                    "organization": org,
                }
            )
            if created:
                user.set_password("demo123")
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {user}"))
        
        # Create Project
        project, created = Project.objects.get_or_create(
            organization=org,
            project_no="PRJ-2024-001",
            defaults={
                "name": "Ethylene Plant Expansion Project",
                "description": "1000 KTPA Ethylene Plant Expansion",
                "status": Project.Status.ACTIVE,
                "hierarchy_config": {
                    "template": "standard",
                    "levels": ["site", "plant", "area", "unit"]
                }
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created project: {project}"))
        
        # Create Client
        client, created = Client.objects.get_or_create(
            project=project,
            code="SINOPEC",
            defaults={
                "name": "Sinopec Engineering Group",
                "contact_person": "Zhang Wei",
                "contact_email": "zhangwei@sinopec.com",
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created client: {client}"))
        
        # Create Site
        site, created = Site.objects.get_or_create(
            client=client,
            code="ZH",
            defaults={
                "name": "Zhenhai Refining & Chemical",
                "location": "Zhenhai, Ningbo, Zhejiang, China",
                "timezone": "Asia/Shanghai",
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created site: {site}"))
        
        # Create Plants
        plants_data = [
            {
                "code": "ETH",
                "name": "Ethylene Plant",
                "description": "1000 KTPA Ethylene Cracker",
                "capacity": "1000 KTPA",
            },
            {
                "code": "ARO",
                "name": "Aromatics Unit",
                "description": "Aromatics Extraction Unit",
                "capacity": "500 KTPA",
            },
        ]
        
        for plant_data in plants_data:
            plant, created = Plant.objects.get_or_create(
                site=site,
                code=plant_data["code"],
                defaults=plant_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created plant: {plant}"))
        
        # Create Naming Conventions
        conventions_data = [
            {
                "name": "ISA-5.1 Standard",
                "description": "Standard ISA-5.1 tag naming convention",
                "hierarchy_format": NamingConvention.HierarchyFormat.UNIT_ONLY,
                "regex_pattern": r"^[A-Z]{2,4}-\d{3}[A-Z]?$",
                "example_tags": ["FT-101", "TIC-201A", "PSV-301"],
                "is_default": True,
            },
            {
                "name": "Full Hierarchy Format",
                "description": "Site-Plant-Area-Unit-Function-Sequence",
                "hierarchy_format": NamingConvention.HierarchyFormat.FULL,
                "regex_pattern": r"^[A-Z]{2}-[A-Z]{3}-\d{3}-U\d{2}-[A-Z]{2,3}-\d{3}$",
                "example_tags": ["ZH-ETH-100-U01-FT-001"],
                "is_default": False,
            },
        ]
        
        for conv_data in conventions_data:
            conv, created = NamingConvention.objects.get_or_create(
                project=project,
                name=conv_data["name"],
                defaults=conv_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created naming convention: {conv}"))
        
        self.stdout.write(self.style.SUCCESS("\nAdministration demo data seeded successfully!"))
        self.stdout.write("\nDemo accounts:")
        self.stdout.write("  admin / admin123 (Administrator)")
        self.stdout.write("  proj_engineer / demo123 (Project Engineer)")
        self.stdout.write("  inst_engineer / demo123 (Instrumentation Engineer)")
        self.stdout.write("  proc_engineer / demo123 (Process Engineer)")
