"""
§15.4.1: project status set Active / OnHold / Completed / Archived
(CANCELLED → ARCHIVED); §15.4.6 / §4.1.11: hierarchy_config gets a validated,
versioned structure (legacy ``levels: ["site", …]`` lists are converted).
"""

from django.db import migrations, models


def forwards(apps, schema_editor):
    from apps.tenants.hierarchy_config import normalize

    ProjectTenant = apps.get_model("tenants", "ProjectTenant")
    ProjectTenant.objects.filter(status="CANCELLED").update(status="ARCHIVED")
    for project in ProjectTenant.objects.exclude(hierarchy_config={}):
        normalized = normalize(project.hierarchy_config, for_new_project=False)
        if normalized != project.hierarchy_config:
            project.hierarchy_config = normalized
            project.save(update_fields=["hierarchy_config"])


def backwards(apps, schema_editor):
    ProjectTenant = apps.get_model("tenants", "ProjectTenant")
    ProjectTenant.objects.filter(status="ARCHIVED").update(status="CANCELLED")


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projecttenant",
            name="status",
            field=models.CharField(
                choices=[
                    ("ACTIVE", "Active"),
                    ("ON_HOLD", "On Hold"),
                    ("COMPLETED", "Completed"),
                    ("ARCHIVED", "Archived"),
                ],
                default="ACTIVE",
                help_text="Project status",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="projecttenant",
            name="hierarchy_config",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="Hierarchy configuration (§15.4.6, schema_version 1)",
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]
