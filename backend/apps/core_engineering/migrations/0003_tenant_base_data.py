"""Data step of the 0002 SPECIFICATION alignment (see 0002 docstring)."""

from django.db import migrations


def forwards_data(apps, schema_editor):
    Tag = apps.get_model("core_engineering", "Tag")
    for tag in Tag.objects.all():
        tag.row_version = max(int(tag.revision or 1), 1)
        if tag.status == "DELETED":
            tag.is_deleted = True
            tag.status = "INACTIVE"
        tag.save(update_fields=["row_version", "is_deleted", "status"])

    # Link PLANT roots to their Plant by code (the former convention) when the
    # match is unambiguous; descendants inherit the plant.
    Plant = apps.get_model("core_engineering", "Plant")
    Node = apps.get_model("core_engineering", "PlantHierarchy")
    linked_plants = set()
    for root in Node.objects.filter(parent__isnull=True):
        candidates = list(Plant.objects.filter(code=root.code))
        if len(candidates) != 1 or candidates[0].pk in linked_plants:
            continue
        plant = candidates[0]
        linked_plants.add(plant.pk)
        Node.objects.filter(tree_id=root.tree_id).update(plant=plant)

    NamingConvention = apps.get_model("core_engineering", "NamingConvention")
    for convention in NamingConvention.objects.all():
        definitions = convention.segment_definitions
        if isinstance(definitions, list) or definitions is None:
            convention.segment_definitions = {"segments": definitions or []}
            convention.save(update_fields=["segment_definitions"])


def backwards_data(apps, schema_editor):
    Tag = apps.get_model("core_engineering", "Tag")
    for tag in Tag.objects.all():
        tag.revision = tag.row_version
        if tag.is_deleted:
            tag.status = "DELETED"
        tag.save(update_fields=["revision", "status"])


class Migration(migrations.Migration):
    dependencies = [
        ("core_engineering", "0002_tenant_base_fields"),
    ]

    operations = [
        migrations.RunPython(forwards_data, backwards_data),
    ]
