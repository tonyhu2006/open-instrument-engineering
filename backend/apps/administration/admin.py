"""
Administration Admin Configuration

Note: Project, Client, Site, Plant, NamingConvention have been moved to tenant-specific apps.
- Project → apps.tenants.models.ProjectTenant
- Client, Site, Plant, NamingConvention → apps.core_engineering.models (tenant schema)
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    Organization,
    Role,
    User,
    ProjectMembership,
    ProjectTaskForce,
    TaskForceMembership,
    AuditLog,
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
        (_("Profile"), {"fields": ("phone", "department", "title", "language", "timezone", "avatar")}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_("Organization"), {"fields": ("organization", "role")}),
    )


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "project_id", "role", "is_active"]
    list_filter = ["is_active", "role"]
    search_fields = ["user__username"]


@admin.register(ProjectTaskForce)
class ProjectTaskForceAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "project_id", "leader", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["code", "name"]


@admin.register(TaskForceMembership)
class TaskForceMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "task_force", "role"]
    search_fields = ["user__username"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["timestamp", "user", "action", "model_name", "object_id"]
    list_filter = ["action", "model_name", "organization"]
    search_fields = ["object_repr", "user__username"]
    ordering = ["-timestamp"]
    readonly_fields = [
        "organization", "project_id", "user", "action", "model_name",
        "object_id", "object_repr", "old_values", "new_values",
        "ip_address", "user_agent", "timestamp"
    ]
