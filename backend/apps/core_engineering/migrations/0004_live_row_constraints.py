"""Constraint step of the 0002 SPECIFICATION alignment (see 0002 docstring)."""

from django.db import migrations, models
from django.db.models import Q

ALIVE = Q(is_deleted=False)


class Migration(migrations.Migration):
    dependencies = [
        ("core_engineering", "0003_tenant_base_data"),
    ]

    operations = [
        migrations.RemoveField(model_name="tag", name="revision"),
        migrations.AlterField(
            model_name="tag",
            name="status",
            field=models.CharField(
                choices=[
                    ("ACTIVE", "Active"),
                    ("INACTIVE", "Inactive"),
                    ("PENDING", "Pending"),
                    ("UNDER_REVIEW", "Under Review"),
                ],
                default="ACTIVE",
                max_length=20,
            ),
        ),
        # --- live-row unique constraints with §4.2.6 codes --------------------
        migrations.AddConstraint(
            model_name="client",
            constraint=models.UniqueConstraint(
                condition=ALIVE,
                fields=("code",),
                name="unique_client_code",
                violation_error_code="ADM_CLIENT_CODE_DUPLICATE",
                violation_error_message="Client code already exists.",
            ),
        ),
        migrations.AddConstraint(
            model_name="site",
            constraint=models.UniqueConstraint(
                condition=ALIVE,
                fields=("client", "code"),
                name="unique_site_code_per_client",
                violation_error_code="ADM_SITE_CODE_DUPLICATE",
                violation_error_message="Site code already exists for this client.",
            ),
        ),
        migrations.AddConstraint(
            model_name="plant",
            constraint=models.UniqueConstraint(
                condition=ALIVE,
                fields=("site", "code"),
                name="unique_plant_code_per_site",
                violation_error_code="ADM_PLANT_CODE_DUPLICATE",
                violation_error_message="Plant code already exists for this site.",
            ),
        ),
        migrations.AddConstraint(
            model_name="planthierarchy",
            constraint=models.UniqueConstraint(
                condition=ALIVE,
                fields=("parent", "code"),
                name="unique_code_per_parent",
                violation_error_code="ADM_HIERARCHY_CODE_DUPLICATE",
                violation_error_message="Code already exists under this parent.",
            ),
        ),
        migrations.AddConstraint(
            model_name="planthierarchy",
            constraint=models.UniqueConstraint(
                condition=Q(parent__isnull=True, is_deleted=False),
                fields=("plant",),
                name="unique_root_per_plant",
                violation_error_code="ADM_HIERARCHY_ROOT_DUPLICATE",
                violation_error_message="This plant already has a root node.",
            ),
        ),
        migrations.AddConstraint(
            model_name="loop",
            constraint=models.UniqueConstraint(
                condition=ALIVE,
                fields=("unit", "loop_tag"),
                name="unique_loop_per_unit",
                violation_error_code="IDX_LOOP_DUPLICATE",
                violation_error_message="Loop number already exists in this unit.",
            ),
        ),
        migrations.AddConstraint(
            model_name="instrumenttype",
            constraint=models.UniqueConstraint(
                condition=ALIVE,
                fields=("code",),
                name="unique_instrument_type_code",
                violation_error_code="IDX_INSTRUMENT_TYPE_DUPLICATE",
                violation_error_message="Instrument type code already exists.",
            ),
        ),
        migrations.AddConstraint(
            model_name="tag",
            constraint=models.UniqueConstraint(
                condition=ALIVE,
                fields=("unit", "tag_number"),
                name="unique_tag_per_unit",
                violation_error_code="IDX_TAG_DUPLICATE",
                violation_error_message="Tag number already exists in this unit.",
            ),
        ),
        migrations.AddConstraint(
            model_name="namingconvention",
            constraint=models.UniqueConstraint(
                condition=Q(is_default=True, is_deleted=False),
                fields=("entity_type",),
                name="unique_default_naming_per_entity",
                violation_error_code="ADM_NAMING_DEFAULT_DUPLICATE",
                violation_error_message=(
                    "Only one default naming convention per entity type."
                ),
            ),
        ),
    ]
