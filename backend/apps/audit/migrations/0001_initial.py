"""
AuditLog moves to the ``audit`` app (§4.10 / §5.5) with the §6.1.1 field set
(UUID id, changed_fields, change_details, batch_id). Existing rows of
``administration.AuditLog`` are copied before that table is dropped by
``administration.0008``.
"""

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def copy_legacy(apps, schema_editor):
    Legacy = apps.get_model("administration", "AuditLog")
    AuditLog = apps.get_model("audit", "AuditLog")
    rows = [
        AuditLog(
            id=uuid.uuid4(),
            organization_id=old.organization_id,
            project_id=old.project_id,
            user_id=old.user_id,
            action=old.action,
            model_name=old.model_name,
            object_id=old.object_id,
            object_repr=old.object_repr,
            old_values=old.old_values,
            new_values=old.new_values,
            changed_fields=sorted(
                k
                for k in set(old.old_values or {}) | set(old.new_values or {})
                if (old.old_values or {}).get(k) != (old.new_values or {}).get(k)
            ),
            change_details={},
            ip_address=old.ip_address,
            user_agent=old.user_agent,
            timestamp=old.timestamp,
        )
        for old in Legacy.objects.all().iterator()
    ]
    AuditLog.objects.bulk_create(rows, batch_size=500)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("administration", "0007_spec_alignment_data"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "project_id",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        help_text="ProjectTenant id (no cross-schema FK)",
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[
                            ("CREATE", "Create"),
                            ("READ", "Read"),
                            ("UPDATE", "Update"),
                            ("DELETE", "Delete"),
                        ],
                        max_length=10,
                    ),
                ),
                ("model_name", models.CharField(max_length=100)),
                ("object_id", models.CharField(max_length=100)),
                ("object_repr", models.CharField(blank=True, max_length=500)),
                ("old_values", models.JSONField(blank=True, default=dict)),
                ("new_values", models.JSONField(blank=True, default=dict)),
                ("changed_fields", models.JSONField(blank=True, default=list)),
                (
                    "change_details",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="§6.1.2 change marker structure",
                    ),
                ),
                (
                    "batch_id",
                    models.UUIDField(
                        blank=True,
                        db_index=True,
                        null=True,
                        help_text="Bulk operation id",
                    ),
                ),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.CharField(blank=True, max_length=500)),
                ("timestamp", models.DateTimeField(auto_now_add=True, db_index=True)),
                (
                    "organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_logs",
                        to="administration.organization",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Audit Log",
                "verbose_name_plural": "Audit Logs",
                "ordering": ["-timestamp"],
                "indexes": [
                    models.Index(
                        fields=["organization", "-timestamp"],
                        name="audit_audit_organiz_idx",
                    ),
                    models.Index(
                        fields=["project_id", "-timestamp"],
                        name="audit_audit_project_idx",
                    ),
                    models.Index(
                        fields=["user", "-timestamp"], name="audit_audit_user_id_idx"
                    ),
                    models.Index(
                        fields=["model_name", "object_id"],
                        name="audit_audit_model_n_idx",
                    ),
                ],
            },
        ),
        migrations.RunPython(copy_legacy, migrations.RunPython.noop),
    ]
