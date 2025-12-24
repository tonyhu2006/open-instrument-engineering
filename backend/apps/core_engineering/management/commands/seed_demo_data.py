"""
Management command to seed demo data for testing.
"""

from django.core.management.base import BaseCommand

from apps.core_engineering.models import PlantHierarchy, Loop, InstrumentType, Tag


class Command(BaseCommand):
    help = "Seed demo data for core engineering models"

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # Create Plant Hierarchy
        plant, _ = PlantHierarchy.objects.get_or_create(
            code="PLANT-001",
            defaults={
                "name": "Demo Chemical Plant",
                "node_type": PlantHierarchy.NodeType.PLANT,
                "description": "Demo plant for testing",
            },
        )
        self.stdout.write(f"  Created Plant: {plant}")

        area_100, _ = PlantHierarchy.objects.get_or_create(
            code="A-100",
            parent=plant,
            defaults={
                "name": "Process Area 100",
                "node_type": PlantHierarchy.NodeType.AREA,
                "description": "Main process area",
            },
        )
        self.stdout.write(f"  Created Area: {area_100}")

        area_200, _ = PlantHierarchy.objects.get_or_create(
            code="A-200",
            parent=plant,
            defaults={
                "name": "Utilities Area 200",
                "node_type": PlantHierarchy.NodeType.AREA,
                "description": "Utilities and support systems",
            },
        )
        self.stdout.write(f"  Created Area: {area_200}")

        unit_110, _ = PlantHierarchy.objects.get_or_create(
            code="U-110",
            parent=area_100,
            defaults={
                "name": "Reactor Unit 110",
                "node_type": PlantHierarchy.NodeType.UNIT,
                "description": "Primary reactor unit",
            },
        )
        self.stdout.write(f"  Created Unit: {unit_110}")

        unit_120, _ = PlantHierarchy.objects.get_or_create(
            code="U-120",
            parent=area_100,
            defaults={
                "name": "Distillation Unit 120",
                "node_type": PlantHierarchy.NodeType.UNIT,
                "description": "Distillation column unit",
            },
        )
        self.stdout.write(f"  Created Unit: {unit_120}")

        # Create Instrument Types with JSON schemas
        flow_transmitter_schema = {
            "type": "object",
            "properties": {
                "range_min": {"type": "number", "description": "Minimum range"},
                "range_max": {"type": "number", "description": "Maximum range"},
                "range_unit": {"type": "string", "description": "Engineering unit"},
                "output_signal": {"type": "string", "enum": ["4-20mA", "HART", "Foundation Fieldbus"]},
                "process_connection": {"type": "string"},
                "material": {"type": "string"},
            },
            "required": ["range_min", "range_max", "range_unit", "output_signal"],
        }

        ft, _ = InstrumentType.objects.get_or_create(
            code="FT",
            defaults={
                "name": "Flow Transmitter",
                "category": InstrumentType.Category.TRANSMITTER,
                "description": "Measures and transmits flow rate",
                "schema_template": flow_transmitter_schema,
                "default_spec_data": {
                    "range_min": 0,
                    "range_max": 100,
                    "range_unit": "m³/h",
                    "output_signal": "4-20mA",
                },
            },
        )
        self.stdout.write(f"  Created InstrumentType: {ft}")

        temp_transmitter_schema = {
            "type": "object",
            "properties": {
                "range_min": {"type": "number"},
                "range_max": {"type": "number"},
                "range_unit": {"type": "string", "enum": ["°C", "°F", "K"]},
                "sensor_type": {"type": "string", "enum": ["RTD", "Thermocouple", "Thermistor"]},
                "output_signal": {"type": "string"},
            },
            "required": ["range_min", "range_max", "range_unit", "sensor_type"],
        }

        tt, _ = InstrumentType.objects.get_or_create(
            code="TT",
            defaults={
                "name": "Temperature Transmitter",
                "category": InstrumentType.Category.TRANSMITTER,
                "description": "Measures and transmits temperature",
                "schema_template": temp_transmitter_schema,
                "default_spec_data": {
                    "range_min": 0,
                    "range_max": 200,
                    "range_unit": "°C",
                    "sensor_type": "RTD",
                    "output_signal": "4-20mA",
                },
            },
        )
        self.stdout.write(f"  Created InstrumentType: {tt}")

        control_valve_schema = {
            "type": "object",
            "properties": {
                "cv": {"type": "number", "description": "Flow coefficient"},
                "body_size": {"type": "string"},
                "body_material": {"type": "string"},
                "trim_material": {"type": "string"},
                "actuator_type": {"type": "string", "enum": ["Pneumatic", "Electric", "Hydraulic"]},
                "fail_position": {"type": "string", "enum": ["FC", "FO", "FL"]},
            },
            "required": ["cv", "body_size", "actuator_type", "fail_position"],
        }

        cv, _ = InstrumentType.objects.get_or_create(
            code="CV",
            defaults={
                "name": "Control Valve",
                "category": InstrumentType.Category.CONTROL_VALVE,
                "description": "Modulating control valve",
                "schema_template": control_valve_schema,
                "default_spec_data": {
                    "cv": 10,
                    "body_size": "2\"",
                    "actuator_type": "Pneumatic",
                    "fail_position": "FC",
                },
            },
        )
        self.stdout.write(f"  Created InstrumentType: {cv}")

        pt, _ = InstrumentType.objects.get_or_create(
            code="PT",
            defaults={
                "name": "Pressure Transmitter",
                "category": InstrumentType.Category.TRANSMITTER,
                "description": "Measures and transmits pressure",
                "schema_template": {
                    "type": "object",
                    "properties": {
                        "range_min": {"type": "number"},
                        "range_max": {"type": "number"},
                        "range_unit": {"type": "string"},
                        "output_signal": {"type": "string"},
                    },
                    "required": ["range_min", "range_max", "range_unit"],
                },
                "default_spec_data": {
                    "range_min": 0,
                    "range_max": 10,
                    "range_unit": "bar",
                    "output_signal": "4-20mA",
                },
            },
        )
        self.stdout.write(f"  Created InstrumentType: {pt}")

        # Create Loops
        fic_101, _ = Loop.objects.get_or_create(
            loop_tag="FIC-101",
            defaults={
                "function": Loop.Function.FLOW,
                "suffix": "101",
                "unit": unit_110,
                "description": "Reactor feed flow control",
            },
        )
        self.stdout.write(f"  Created Loop: {fic_101}")

        tic_102, _ = Loop.objects.get_or_create(
            loop_tag="TIC-102",
            defaults={
                "function": Loop.Function.TEMPERATURE,
                "suffix": "102",
                "unit": unit_110,
                "description": "Reactor temperature control",
            },
        )
        self.stdout.write(f"  Created Loop: {tic_102}")

        # Create Tags
        ft_101, _ = Tag.objects.get_or_create(
            tag_number="FT-101",
            unit=unit_110,
            defaults={
                "loop": fic_101,
                "instrument_type": ft,
                "service": "Reactor feed flow measurement",
                "spec_data": {
                    "range_min": 0,
                    "range_max": 150,
                    "range_unit": "m³/h",
                    "output_signal": "4-20mA",
                    "process_connection": "2\" 150# RF",
                    "material": "316SS",
                },
            },
        )
        self.stdout.write(f"  Created Tag: {ft_101}")

        fv_101, _ = Tag.objects.get_or_create(
            tag_number="FV-101",
            unit=unit_110,
            defaults={
                "loop": fic_101,
                "instrument_type": cv,
                "service": "Reactor feed flow control valve",
                "spec_data": {
                    "cv": 25,
                    "body_size": "3\"",
                    "body_material": "WCB",
                    "trim_material": "316SS",
                    "actuator_type": "Pneumatic",
                    "fail_position": "FC",
                },
            },
        )
        self.stdout.write(f"  Created Tag: {fv_101}")

        tt_102, _ = Tag.objects.get_or_create(
            tag_number="TT-102",
            unit=unit_110,
            defaults={
                "loop": tic_102,
                "instrument_type": tt,
                "service": "Reactor temperature measurement",
                "spec_data": {
                    "range_min": 0,
                    "range_max": 300,
                    "range_unit": "°C",
                    "sensor_type": "RTD",
                    "output_signal": "4-20mA",
                },
            },
        )
        self.stdout.write(f"  Created Tag: {tt_102}")

        pt_103, _ = Tag.objects.get_or_create(
            tag_number="PT-103",
            unit=unit_110,
            defaults={
                "instrument_type": pt,
                "service": "Reactor pressure measurement",
                "spec_data": {
                    "range_min": 0,
                    "range_max": 25,
                    "range_unit": "bar",
                    "output_signal": "4-20mA",
                },
            },
        )
        self.stdout.write(f"  Created Tag: {pt_103}")

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
