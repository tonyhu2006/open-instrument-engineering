"""
Seed a second demo project to verify multi-tenant schema isolation.

Creates a `ProjectTenant` (which auto-creates a PostgreSQL schema), then
populates the project schema with a Client → Site → Plant hierarchy that is
completely independent from any other project's data.

Usage:
    python manage.py seed_demo_project
    python manage.py seed_demo_project --project-no PRJ-2025-002 --name "Refinery Upgrade"
"""

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from apps.administration.models import Organization
from apps.core_engineering.models import Client, Plant, Site
from apps.tenants.models import ProjectTenant

# Distinctive sample payloads so it is obvious in the UI that the two
# projects' data are physically isolated (different clients, sites, plants).
DEFAULT_PAYLOAD = {
    "project_no": "PRJ-2025-002",
    "name": "LNG Receiving Terminal Project",
    "description": "Coastal LNG receiving terminal — used to validate tenant schema isolation",
    "client": {
        "code": "CNPC",
        "name": "China National Petroleum Corporation",
        "contact_person": "Li Ming",
        "contact_email": "liming@cnpc.cn",
        "contact_phone": "+86-10-8888-0001",
        "address": "Beijing, China",
    },
    "site": {
        "code": "TJ",
        "name": "Tianjin LNG Terminal",
        "location": "Tianjin Port, China",
        "address": "Binhai New Area, Tianjin",
        "timezone": "Asia/Shanghai",
    },
    "plants": [
        {
            "code": "REGAS",
            "name": "Regasification Unit",
            "description": "LNG regas unit",
            "capacity": "6.5 MTPA",
        },
        {
            "code": "STORAGE",
            "name": "LNG Storage Tanks",
            "description": "4x160,000m³ tanks",
            "capacity": "640,000 m³",
        },
    ],
}


class Command(BaseCommand):
    help = "Seed a second demo project tenant to verify schema isolation."

    def add_arguments(self, parser):
        parser.add_argument("--project-no", default=DEFAULT_PAYLOAD["project_no"])
        parser.add_argument("--name", default=DEFAULT_PAYLOAD["name"])
        parser.add_argument(
            "--org",
            default=None,
            help="Organization code that owns the project. Defaults to the first org.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Pick organization
        org_code = options.get("org")
        if org_code:
            try:
                org = Organization.objects.get(code=org_code)
            except Organization.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(f"Organization '{org_code}' not found.")
                )
                return
        else:
            org = Organization.objects.first()
            if not org:
                self.stderr.write(
                    self.style.ERROR(
                        "No organization exists. Run `seed_rbac --create-org` first or "
                        "create one via the Administration UI."
                    )
                )
                return

        project_no = options["project_no"]
        name = options["name"]

        # Create or fetch ProjectTenant — django-tenants auto-creates the schema
        # and runs migrations for TENANT_APPS into the new schema.
        tenant, created = ProjectTenant.objects.get_or_create(
            project_no=project_no,
            defaults={
                "name": name,
                "description": DEFAULT_PAYLOAD["description"],
                "organization_id": org.id,
                "status": ProjectTenant.Status.ACTIVE,
                "hierarchy_config": {
                    "template": "standard",
                    "levels": ["site", "plant", "area", "unit"],
                },
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created tenant: pk={tenant.pk} schema={tenant.schema_name} "
                    f"({tenant.project_no})"
                )
            )
        else:
            self.stdout.write(f"Tenant already exists: schema={tenant.schema_name}")

        # Switch into the new schema and seed tenant-local data
        connection.set_tenant(tenant)
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f"\nSeeding data into schema '{tenant.schema_name}'..."
            )
        )

        client_data = DEFAULT_PAYLOAD["client"]
        client, c_created = Client.objects.get_or_create(
            code=client_data["code"],
            defaults={k: v for k, v in client_data.items() if k != "code"},
        )
        self.stdout.write(
            ("  + " if c_created else "  = ") + f"Client {client.code} - {client.name}"
        )

        site_data = DEFAULT_PAYLOAD["site"]
        site, s_created = Site.objects.get_or_create(
            client=client,
            code=site_data["code"],
            defaults={k: v for k, v in site_data.items() if k != "code"},
        )
        self.stdout.write(
            ("  + " if s_created else "  = ") + f"Site   {site.code} - {site.name}"
        )

        for plant_data in DEFAULT_PAYLOAD["plants"]:
            plant, p_created = Plant.objects.get_or_create(
                site=site,
                code=plant_data["code"],
                defaults={k: v for k, v in plant_data.items() if k != "code"},
            )
            self.stdout.write(
                ("  + " if p_created else "  = ")
                + f"Plant  {plant.code} - {plant.name}"
            )

        # Restore public schema
        connection.set_schema_to_public()

        self.stdout.write(
            self.style.SUCCESS(
                "\nDone. Two tenants now exist; their data lives in physically "
                "separate PostgreSQL schemas. Switch projects via the UI's project "
                "selector to verify isolation."
            )
        )
