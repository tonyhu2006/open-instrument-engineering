"""
SPECIFICATION Module 15 alignment — constraint step, and removal of the
legacy AuditLog table (moved to ``apps.audit`` by ``audit.0001``).
"""

from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("administration", "0007_spec_alignment_data"),
        ("audit", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organization",
            name="slug",
            field=models.SlugField(
                blank=True,
                max_length=60,
                unique=True,
                help_text="URL-friendly identifier (derived from code when empty)",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="projecttaskforce",
            name="unique_task_force_code_per_project",
        ),
        migrations.AlterField(
            model_name="projecttaskforce",
            name="code",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AddConstraint(
            model_name="projecttaskforce",
            constraint=models.UniqueConstraint(
                condition=Q(project_id__isnull=False),
                fields=("project_id",),
                name="unique_task_force_per_project",
                violation_error_code="ADM_TASK_FORCE_PROJECT_TAKEN",
                violation_error_message=(
                    "This project already has a task force (one per project)."
                ),
            ),
        ),
        migrations.RemoveField(model_name="taskforcemembership", name="role"),
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                condition=~Q(email=""),
                fields=("email",),
                name="unique_user_email",
                violation_error_code="ADM_USER_EMAIL_DUPLICATE",
                violation_error_message="A user with this email already exists.",
            ),
        ),
        migrations.DeleteModel(name="AuditLog"),
    ]
