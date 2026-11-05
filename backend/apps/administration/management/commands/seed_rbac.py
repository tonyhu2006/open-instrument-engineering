"""
Refresh the 7 RBAC system roles (§15.2.2, decision D5) of every organization.

The roles themselves are delivered by data migration
``administration.0007_seed_system_roles`` and created automatically for new
organizations by ``OrganizationService``; this command re-applies the
definitions in ``apps/administration/rbac.py`` (idempotent).

Usage:
    python manage.py seed_rbac
    python manage.py seed_rbac --org DEMO
    python manage.py seed_rbac --create-org
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.administration.models import Organization, Role
from apps.administration.rbac import ensure_system_roles


class Command(BaseCommand):
    help = "Create/refresh the 7 system roles of each organization."

    def add_arguments(self, parser):
        parser.add_argument("--org", default=None, help="Organization code")
        parser.add_argument(
            "--create-org",
            action="store_true",
            help="Create a DEMO organization when none exists.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        orgs = Organization.objects.all()
        if options["org"]:
            orgs = orgs.filter(code=options["org"])
            if not orgs.exists():
                raise CommandError(f"Organization '{options['org']}' not found.")
        if not orgs.exists() and options["create_org"]:
            Organization.objects.create(code="DEMO", name="Demo Engineering Company")
            orgs = Organization.objects.all()
        for org in orgs:
            roles = ensure_system_roles(org, Role)
            self.stdout.write(f"{org.code}: {len(roles)} system roles up to date")
