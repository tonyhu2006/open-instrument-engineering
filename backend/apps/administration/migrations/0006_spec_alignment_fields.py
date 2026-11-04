"""
SPECIFICATION Module 15 alignment — schema step (nullable / non-unique first;
data in 0007, constraints in 0008):

* §15.4.7 Organization.slug / settings
* §15.2.3 User.employee_id; role is PROTECTed (every user needs one)
* §15.3.1 ProjectTaskForce.created_by / created_by_role, project optional
* §15.3.1 TaskForceMembership.role_in_project / joined_at / added_by / is_active
"""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("administration", "0005_user_ui_preferences"),
    ]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="settings",
            field=models.JSONField(
                blank=True, default=dict, help_text="Organization-level configuration"
            ),
        ),
        migrations.AddField(
            model_name="organization",
            name="slug",
            field=models.SlugField(
                blank=True,
                default="",
                max_length=60,
                help_text="URL-friendly identifier (derived from code when empty)",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="user",
            name="employee_id",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="users",
                to="administration.role",
                help_text="System role (required for every API-managed user)",
            ),
        ),
        migrations.AlterField(
            model_name="projecttaskforce",
            name="project_id",
            field=models.IntegerField(
                blank=True,
                null=True,
                help_text=(
                    "ProjectTenant id (tenants.ProjectTenant); one group per project"
                ),
            ),
        ),
        migrations.AddField(
            model_name="projecttaskforce",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="created_task_forces",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="projecttaskforce",
            name="created_by_role",
            field=models.CharField(
                blank=True,
                choices=[
                    ("ADMINISTRATOR", "Administrator"),
                    ("PROJECT_MANAGER", "Project Manager"),
                    ("PROJECT_ENGINEER", "Project Engineer"),
                ],
                max_length=20,
            ),
        ),
        migrations.AlterModelOptions(
            name="projecttaskforce",
            options={
                "ordering": ["code"],
                "verbose_name": "Project Task Force",
                "verbose_name_plural": "Project Task Forces",
            },
        ),
        migrations.AddField(
            model_name="taskforcemembership",
            name="role_in_project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="project_memberships",
                to="administration.role",
                help_text="Overrides the user's system role inside this project",
            ),
        ),
        migrations.AddField(
            model_name="taskforcemembership",
            name="joined_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="taskforcemembership",
            name="added_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="added_task_force_memberships",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="taskforcemembership",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
