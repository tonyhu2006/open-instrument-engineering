"""
Administration Models - Multi-tenancy, Project Hierarchy, RBAC

This module implements:
- Organization (multi-tenant isolation)
- Project hierarchy (Project → Client → Site → Plant)
- Role-based access control (RBAC)
- Project Task Force (team management)
- Naming Conventions
"""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
import re

from apps.core.models import TimeStampedModel


# =============================================================================
# Multi-Tenancy Models
# =============================================================================

class Organization(TimeStampedModel):
    """
    Organization - Top-level tenant for SaaS multi-tenancy.
    All data is isolated at the organization level.
    """
    
    name = models.CharField(
        max_length=200,
        help_text=_("Organization name"),
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Unique organization code (e.g., 'ACME', 'SINOPEC')"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Organization description"),
    )
    logo = models.ImageField(
        upload_to="organizations/logos/",
        blank=True,
        null=True,
        help_text=_("Organization logo"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this organization is active"),
    )
    
    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        ordering = ["name"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# =============================================================================
# Note: Project hierarchy models moved to tenant-specific apps
# =============================================================================
# - Project → apps.tenants.models.ProjectTenant (tenant model)
# - Client, Site, Plant → apps.core_engineering.models (tenant schema)
# =============================================================================


# =============================================================================
# RBAC Models (Shared - stored in public schema)
# =============================================================================

class Role(TimeStampedModel):
    """
    Role - Defines user roles with hierarchical levels.
    Level 5 is highest (Administrator), Level 1 is lowest (Guest).
    """
    
    class Level(models.IntegerChoices):
        GUEST = 1, _("Guest")
        ENGINEER_L2 = 2, _("Engineer Level 2")
        ENGINEER_L3 = 3, _("Engineer Level 3")
        PROJECT_ENGINEER = 4, _("Project Engineer")
        ADMINISTRATOR = 5, _("Administrator")
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="roles",
        help_text=_("Organization this role belongs to"),
    )
    name = models.CharField(
        max_length=100,
        help_text=_("Role name (e.g., 'Instrumentation Engineer')"),
    )
    code = models.CharField(
        max_length=50,
        help_text=_("Role code (e.g., 'INST_ENG', 'PROC_ENG')"),
    )
    level = models.IntegerField(
        choices=Level.choices,
        default=Level.GUEST,
        help_text=_("Role hierarchy level (1-5)"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Role description"),
    )
    permissions = models.JSONField(
        default=dict,
        blank=True,
        help_text=_(
            "Permission matrix. Example: "
            "{'tag': ['create', 'read', 'update'], 'loop': ['read']}"
        ),
    )
    is_system_role = models.BooleanField(
        default=False,
        help_text=_("System roles cannot be deleted"),
    )
    
    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ["-level", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_role_code_per_org",
            ),
        ]
    
    def __str__(self):
        return f"{self.name} (Level {self.level})"


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds organization membership and role assignment.
    """
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        help_text=_("Primary organization"),
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        help_text=_("User's role"),
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Phone number"),
    )
    department = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Department"),
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Job title"),
    )
    language = models.CharField(
        max_length=10,
        default="en",
        help_text=_("Preferred language (e.g., 'en', 'zh-CN')"),
    )
    timezone = models.CharField(
        max_length=50,
        default="UTC",
        help_text=_("User timezone"),
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        help_text=_("User avatar"),
    )
    
    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def has_permission(self, model_name: str, action: str) -> bool:
        """Check if user has permission for a specific action on a model."""
        if not self.role:
            return False
        
        # Administrators have all permissions
        if self.role.level == Role.Level.ADMINISTRATOR:
            return True
        
        permissions = self.role.permissions.get(model_name, [])
        return action in permissions


class ProjectMembership(TimeStampedModel):
    """
    ProjectMembership - Links users to projects with specific roles.
    A user can have different roles in different projects.
    Uses project_id (integer) to reference ProjectTenant without cross-schema FK.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_memberships",
        help_text=_("User"),
    )
    project_id = models.IntegerField(
        default=0,
        help_text=_("ProjectTenant ID (references tenants.ProjectTenant)"),
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="project_memberships",
        help_text=_("Role in this project"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this membership is active"),
    )
    
    class Meta:
        verbose_name = _("Project Membership")
        verbose_name_plural = _("Project Memberships")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project_id"],
                name="unique_user_project_membership",
            ),
        ]
    
    def __str__(self):
        return f"{self.user} - Project {self.project_id} ({self.role})"
    
    @property
    def project(self):
        """Get the ProjectTenant instance."""
        from apps.tenants.models import ProjectTenant
        return ProjectTenant.objects.filter(pk=self.project_id).first()


# =============================================================================
# Project Task Force
# =============================================================================

class ProjectTaskForce(TimeStampedModel):
    """
    ProjectTaskForce - Team/group within a project.
    Provides data isolation between different teams.
    Uses project_id (integer) to reference ProjectTenant without cross-schema FK.
    """
    
    project_id = models.IntegerField(
        default=0,
        help_text=_("ProjectTenant ID (references tenants.ProjectTenant)"),
    )
    name = models.CharField(
        max_length=200,
        help_text=_("Task force name"),
    )
    code = models.CharField(
        max_length=50,
        help_text=_("Task force code"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Task force description"),
    )
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_task_forces",
        help_text=_("Task force leader"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this task force is active"),
    )
    
    class Meta:
        verbose_name = _("Project Task Force")
        verbose_name_plural = _("Project Task Forces")
        constraints = [
            models.UniqueConstraint(
                fields=["project_id", "code"],
                name="unique_task_force_code_per_project",
            ),
        ]
    
    def __str__(self):
        return f"Project {self.project_id} - {self.name}"
    
    @property
    def project(self):
        """Get the ProjectTenant instance."""
        from apps.tenants.models import ProjectTenant
        return ProjectTenant.objects.filter(pk=self.project_id).first()


class TaskForceMembership(TimeStampedModel):
    """
    TaskForceMembership - Links users to task forces.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_force_memberships",
        help_text=_("User"),
    )
    task_force = models.ForeignKey(
        ProjectTaskForce,
        on_delete=models.CASCADE,
        related_name="memberships",
        help_text=_("Task force"),
    )
    role = models.CharField(
        max_length=50,
        default="member",
        help_text=_("Role in task force (e.g., 'leader', 'member')"),
    )
    
    class Meta:
        verbose_name = _("Task Force Membership")
        verbose_name_plural = _("Task Force Memberships")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "task_force"],
                name="unique_user_task_force_membership",
            ),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.task_force}"


# =============================================================================
# Note: NamingConvention moved to apps.core_engineering.models (tenant schema)
# =============================================================================


# =============================================================================
# Audit Log (Shared - stored in public schema)
# =============================================================================

class AuditLog(models.Model):
    """
    AuditLog - Records all data operations (Who/When/What).
    Stored in public schema for cross-project audit trail.
    """
    
    class Action(models.TextChoices):
        CREATE = "CREATE", _("Create")
        READ = "READ", _("Read")
        UPDATE = "UPDATE", _("Update")
        DELETE = "DELETE", _("Delete")
    
    id = models.BigAutoField(primary_key=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        null=True,
        blank=True,
        help_text=_("Organization"),
    )
    project_id = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("ProjectTenant ID (if applicable)"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
        help_text=_("User who performed the action"),
    )
    action = models.CharField(
        max_length=10,
        choices=Action.choices,
        help_text=_("Action performed"),
    )
    model_name = models.CharField(
        max_length=100,
        help_text=_("Model name (e.g., 'Tag', 'Loop')"),
    )
    object_id = models.CharField(
        max_length=100,
        help_text=_("ID of the affected object"),
    )
    object_repr = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("String representation of the object"),
    )
    old_values = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Values before the change"),
    )
    new_values = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Values after the change"),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_("Client IP address"),
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Client user agent"),
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When the action occurred"),
    )
    
    class Meta:
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["organization", "-timestamp"]),
            models.Index(fields=["project_id", "-timestamp"]),
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["model_name", "object_id"]),
        ]
    
    def __str__(self):
        return f"{self.user} {self.action} {self.model_name}:{self.object_id}"
    
    @property
    def project(self):
        """Get the ProjectTenant instance."""
        if self.project_id:
            from apps.tenants.models import ProjectTenant
            return ProjectTenant.objects.filter(pk=self.project_id).first()
        return None
