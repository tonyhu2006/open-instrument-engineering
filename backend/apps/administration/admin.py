"""
Administration Admin Configuration

Note: Project, Client, Site, Plant, NamingConvention have been moved to
tenant-specific apps.
- Project → apps.tenants.models.ProjectTenant
- Client, Site, Plant, NamingConvention → apps.core_engineering.models (tenant schema)
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    Organization,
    ProjectTaskForce,
    Role,
    TaskForceMembership,
    User,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["code", "name"]
    ordering = ["name"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "organization", "level", "is_system_role"]
    list_filter = ["level", "organization", "is_system_role"]
    search_fields = ["name", "code"]
    ordering = ["-level", "name"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "organization", "role", "is_active"]
    list_filter = ["is_active", "is_staff", "organization", "role"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["username"]

    fieldsets = BaseUserAdmin.fieldsets + (
        (_("Organization"), {"fields": ("organization", "role")}),
        (
            _("Profile"),
            {
                "fields": (
                    "employee_id",
                    "phone",
                    "department",
                    "title",
                    "language",
                    "timezone",
                    "avatar",
                )
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_("Organization"), {"fields": ("organization", "role")}),
    )


@admin.register(ProjectTaskForce)
class ProjectTaskForceAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "project_id", "leader", "created_by", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["code", "name"]


@admin.register(TaskForceMembership)
class TaskForceMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "task_force", "role_in_project", "is_active"]
    search_fields = ["user__username"]
