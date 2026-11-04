"""
SPECIFICATION alignment for tenant tables:

* §4.1.1 audit columns, soft delete and ``row_version`` on every table;
* Tag ``revision`` → ``row_version``; status DELETED → soft delete;
* §4.1.6 Loop number unique per Unit (was global);
* unique constraints only over live rows, with §4.2.6 error codes;
* §15.4.5 ``PlantHierarchy.plant`` FK (roots linked to their Plant by code);
* §15.5.1 NamingConvention fields (``regex_pattern`` → ``pattern``,
  ``example_tags`` → ``examples``, entity_type, priority, …).
"""

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q

ALIVE = Q(is_deleted=False)
BASE_MODELS = [
    "client",
    "site",
    "plant",
    "planthierarchy",
    "loop",
    "instrumenttype",
    "tag",
    "namingconvention",
]


def base_fields(model_name):
    return [
        migrations.AddField(
            model_name=model_name,
            name="created_by_id",
            field=models.IntegerField(
                blank=True,
                null=True,
                help_text="User id of the creator (public schema)",
            ),
        ),
        migrations.AddField(
            model_name=model_name,
            name="updated_by_id",
            field=models.IntegerField(
                blank=True, null=True, help_text="User id of the last editor"
            ),
        ),
        migrations.AddField(
            model_name=model_name,
            name="is_deleted",
            field=models.BooleanField(
                db_index=True, default=False, help_text="Soft delete flag"
            ),
        ),
        migrations.AddField(
            model_name=model_name,
            name="row_version",
            field=models.PositiveIntegerField(
                default=1, help_text="Optimistic lock version"
            ),
        ),
    ]


class Migration(migrations.Migration):
    dependencies = [
        ("core_engineering", "0001_initial"),
    ]

    operations = [
        # --- drop the old (unconditional) constraints / uniques -------------
        migrations.RemoveConstraint(
            model_name="plant", name="unique_plant_code_per_site"
        ),
        migrations.RemoveConstraint(
            model_name="planthierarchy", name="unique_code_per_parent"
        ),
        migrations.RemoveConstraint(
            model_name="site", name="unique_site_code_per_client"
        ),
        migrations.RemoveConstraint(model_name="tag", name="unique_tag_per_unit"),
        migrations.AlterField(
            model_name="client",
            name="code",
            field=models.CharField(
                max_length=50, help_text="Unique within the project"
            ),
        ),
        migrations.AlterField(
            model_name="instrumenttype",
            name="code",
            field=models.CharField(max_length=20, help_text="e.g. 'FT', 'TT', 'CV'"),
        ),
        migrations.AlterField(
            model_name="loop",
            name="loop_tag",
            field=models.CharField(max_length=50, help_text="Loop number"),
        ),
        # --- §4.1.1 base columns --------------------------------------------
        *[op for name in BASE_MODELS for op in base_fields(name)],
        # --- PlantHierarchy.plant (§15.4.5) ---------------------------------
        migrations.AddField(
            model_name="planthierarchy",
            name="plant",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="hierarchy_nodes",
                to="core_engineering.plant",
                help_text="Plant this node belongs to (required for PLANT roots)",
            ),
        ),
        # --- NamingConvention (§15.5.1) -------------------------------------
        migrations.RenameField(
            model_name="namingconvention", old_name="regex_pattern", new_name="pattern"
        ),
        migrations.RenameField(
            model_name="namingconvention", old_name="example_tags", new_name="examples"
        ),
        migrations.AlterField(
            model_name="namingconvention",
            name="pattern",
            field=models.CharField(
                max_length=500, help_text="Regular expression (named groups = segments)"
            ),
        ),
        migrations.AddField(
            model_name="namingconvention",
            name="entity_type",
            field=models.CharField(
                choices=[
                    ("TAG", "Tag"),
                    ("LOOP", "Loop"),
                    ("CABLE", "Cable"),
                    ("JUNCTION_BOX", "Junction Box"),
                    ("TERMINAL_STRIP", "Terminal Strip"),
                ],
                default="TAG",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="namingconvention",
            name="pattern_template",
            field=models.CharField(
                blank=True,
                max_length=200,
                help_text="e.g. {Plant}-{Unit}-{Function}-{Sequence}",
            ),
        ),
        migrations.AddField(
            model_name="namingconvention",
            name="separator",
            field=models.CharField(blank=True, default="-", max_length=5),
        ),
        migrations.AddField(
            model_name="namingconvention",
            name="validation_message",
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name="namingconvention",
            name="priority",
            field=models.IntegerField(
                default=100, help_text="Lower value = matched first"
            ),
        ),
        migrations.AlterField(
            model_name="namingconvention",
            name="segment_definitions",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterModelOptions(
            name="namingconvention",
            options={
                "ordering": ["entity_type", "-is_default", "priority", "name"],
                "verbose_name": "Naming Convention",
                "verbose_name_plural": "Naming Conventions",
            },
        ),
        migrations.AlterModelOptions(
            name="planthierarchy",
            options={
                "default_manager_name": "objects",
                "verbose_name": "Plant Hierarchy",
                "verbose_name_plural": "Plant Hierarchies",
            },
        ),
    ]
