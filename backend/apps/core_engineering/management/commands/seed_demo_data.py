"""
Tenant-schema demo data — SPECIFICATION §4.8.1 (engineering part).

Runs inside the demo project's schema (``PRJ-DEMO-001`` by default, created by
``seed_admin_data``) and creates, idempotently:

* Client DEMO_OWNER → Site S1 → Plant P1 → Area A101 → Unit U101
* Instrument types FE, FT, FV, PT, TT, LT, XV, ZS, AI, AO, DI, DO
* Loop 101-F-100 with tags 101-FE-100, 101-FT-100, 101-FV-100

Usage::

    python manage.py seed_demo_data
    python manage.py seed_demo_data --project-no PRJ-2025-002
"""

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from apps.core_engineering.models import (
    Client,
    InstrumentType,
    Loop,
    Plant,
    PlantHierarchy,
    Site,
    Tag,
)
from apps.core_engineering.services import (
    ClientService,
    InstrumentTypeService,
    LoopService,
    PlantHierarchyService,
    PlantService,
    SiteService,
    TagService,
)
from apps.tenants.models import ProjectTenant

INSTRUMENT_TYPES = [
    ("FE", "Flow Element", "SENSOR"),
    ("FT", "Flow Transmitter", "TRANSMITTER"),
    ("FV", "Flow Control Valve", "CONTROL_VALVE"),
    ("PT", "Pressure Transmitter", "TRANSMITTER"),
    ("TT", "Temperature Transmitter", "TRANSMITTER"),
    ("LT", "Level Transmitter", "TRANSMITTER"),
    ("XV", "On/Off Valve", "CONTROL_VALVE"),
    ("ZS", "Position Switch", "SWITCH"),
    ("AI", "Analog Input", "OTHER"),
    ("AO", "Analog Output", "OTHER"),
    ("DI", "Digital Input", "OTHER"),
    ("DO", "Digital Output", "OTHER"),
]

FT_SCHEMA = {
    "type": "object",
    "properties": {
        "range_min": {"type": "number"},
        "range_max": {"type": "number"},
        "range_unit": {"type": "string"},
        "output_signal": {"type": "string"},
    },
}


def _get_or_create(model, service, lookup, values):
    existing = model.alive.filter(**lookup).first()
    if existing is not None:
        return existing, False
    return service.create({**lookup, **values}), True


class Command(BaseCommand):
    help = "Seed tenant-schema demo data (§4.8.1) into a project schema."

    def add_arguments(self, parser):
        parser.add_argument("--project-no", default="PRJ-DEMO-001")

    def handle(self, *args, **options):
        project = ProjectTenant.objects.filter(project_no=options["project_no"]).first()
        if project is None:
            raise CommandError(
                f"Project {options['project_no']} not found; "
                "run seed_admin_data first."
            )
        with schema_context(project.schema_name):
            self._seed()
        self.stdout.write(
            self.style.SUCCESS(f"Demo data ready in schema {project.schema_name}")
        )

    def _seed(self):
        client, _ = _get_or_create(
            Client, ClientService(), {"code": "DEMO_OWNER"}, {"name": "Demo Owner"}
        )
        site, _ = _get_or_create(
            Site, SiteService(), {"client": client, "code": "S1"}, {"name": "Site 1"}
        )
        plant, _ = _get_or_create(
            Plant, PlantService(), {"site": site, "code": "P1"}, {"name": "Plant 1"}
        )
        root = PlantHierarchy.alive.get(plant=plant, parent__isnull=True)
        hierarchy = PlantHierarchyService()
        area, _ = _get_or_create(
            PlantHierarchy,
            hierarchy,
            {"parent": root, "code": "A101"},
            {"name": "Area 101", "node_type": PlantHierarchy.NodeType.AREA},
        )
        unit, _ = _get_or_create(
            PlantHierarchy,
            hierarchy,
            {"parent": area, "code": "U101"},
            {"name": "Unit 101", "node_type": PlantHierarchy.NodeType.UNIT},
        )
        self.stdout.write(f"  Hierarchy: {unit.full_path}")

        types = {}
        for code, name, category in INSTRUMENT_TYPES:
            types[code], _ = _get_or_create(
                InstrumentType,
                InstrumentTypeService(),
                {"code": code},
                {
                    "name": name,
                    "category": category,
                    "schema_template": FT_SCHEMA if code == "FT" else {},
                },
            )
        self.stdout.write(f"  Instrument types: {len(types)}")

        loop, _ = _get_or_create(
            Loop,
            LoopService(),
            {"unit": unit, "loop_tag": "101-F-100"},
            {"function": Loop.Function.FLOW, "description": "Feed flow control"},
        )
        for code, service in [
            ("FE", "Feed flow element"),
            ("FT", "Feed flow transmitter"),
            ("FV", "Feed flow control valve"),
        ]:
            _get_or_create(
                Tag,
                TagService(),
                {"unit": unit, "tag_number": f"101-{code}-100"},
                {"loop": loop, "instrument_type": types[code], "service": service},
            )
        self.stdout.write("  Loop 101-F-100 with 101-FE/FT/FV-100")
