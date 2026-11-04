"""
Administration Models (public schema) — SPECIFICATION Module 15.

- Organization (§15.4.7)
- Role / User (RBAC, §15.2)
- ProjectTaskForce / TaskForceMembership (§15.3)

AuditLog lives in ``apps.audit`` (§4.10 / §5.5); tenant-schema project data
(Client/Site/Plant/PlantHierarchy/NamingConvention) lives in
``apps.core_engineering``.
"""

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel

# =============================================================================
# Organization (§15.4.7 — optional SaaS-level tenant)
# =============================================================================


class Organization(TimeStampedModel):
    """Design institute / engineering company owning projects and roles."""

    name = models.CharField(max_length=200, help_text=_("Organization name"))
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Unique organization code (e.g., 'ACME', 'SINOPEC')"),
    )
    slug = models.SlugField(
        max_length=60,
        unique=True,
        blank=True,
        help_text=_("URL-friendly identifier (derived from code when empty)"),
    )
    description = models.TextField(blank=True, help_text=_("Description"))
    logo = models.ImageField(
        upload_to="organizations/logos/",
        blank=True,
        null=True,
        help_text=_("Organization logo"),
    )
    settings = models.JSONField(
        default=dict, blank=True, help_text=_("Organization-level configuration")
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = (
                slugify(self.code, allow_unicode=True)[:60]
                or f"org-{uuid.uuid4().hex[:12]}"
            )
        super().save(*args, **kwargs)


# =============================================================================
# RBAC (§15.2)
# =============================================================================


class Role(TimeStampedModel):
    """Role = job function, ``level`` = authority axis (decision D5).

    Five levels (Level 2 reserved), seven system roles (see ``rbac.py``).
    Authorization is decided by the ``permissions`` matrix.
    """

    class Level(models.IntegerChoices):
        GUEST = 1, _("Guest")
        ENGINEER_L2 = 2, _("Engineer Level 2")
        ENGINEER_L3 = 3, _("Engineer Level 3")
        PROJECT_ENGINEER = 4, _("Project Engineer")
        ADMINISTRATOR = 5, _("Administrator")

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="roles"
    )
    name = models.CharField(max_length=100, help_text=_("Display name"))
    code = models.CharField(
        max_length=50, help_text=_("Stable identifier, unique within organization")
    )
    level = models.IntegerField(choices=Level.choices, default=Level.GUEST)
    description = models.TextField(blank=True)
    permissions = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Permission matrix {resource: [create|read|update|delete]}"),
    )
    is_system_role = models.BooleanField(
        default=False, help_text=_("System roles cannot be deleted")
    )
    display_order = models.IntegerField(
        default=100, help_text=_("Tie-breaker within the same level")
    )

    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ["-level", "display_order", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "code"],
                name="unique_role_code_per_org",
            ),
        ]

    def __str__(self):
        return f"{self.name} (Level {self.level})"

    def clean(self):
        """§4.1.5: the permission matrix is schema-driven — reject unknown
        resources or actions."""
        from django.core.exceptions import ValidationError

        from .rbac import ACTIONS, RESOURCES

        super().clean()
        matrix = self.permissions or {}
        if not isinstance(matrix, dict):
            raise ValidationError({"permissions": _("Must be a JSON object.")})
        errors = []
        for resource, actions in matrix.items():
            if resource != "*" and resource not in RESOURCES:
                errors.append(f"Unknown resource '{resource}'.")
                continue
            if not isinstance(actions, list) or any(a not in ACTIONS for a in actions):
                errors.append(
                    f"Actions of '{resource}' must be a subset of {list(ACTIONS)}."
                )
        if errors:
            raise ValidationError({"permissions": errors})


class User(AbstractUser):
    """Custom user (§15.2.3)."""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
        help_text=_("System role (required for every API-managed user)"),
    )
    employee_id = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=200, blank=True)
    title = models.CharField(max_length=200, blank=True)
    language = models.CharField(
        max_length=10, default="en", help_text=_("Preferred language")
    )
    timezone = models.CharField(max_length=50, default="UTC")
    avatar = models.ImageField(upload_to="users/avatars/", blank=True, null=True)
    ui_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("User preferences (I18N-04 / ADM-06)"),
    )

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=~Q(email=""),
                name="unique_user_email",
                violation_error_code="ADM_USER_EMAIL_DUPLICATE",
                violation_error_message=_("A user with this email already exists."),
            ),
        ]

    def __str__(self):
        return self.get_full_name() or self.username

    def has_permission(self, model_name: str, action: str, project_id=None) -> bool:
        """Matrix check (§15.2.4); see ``access.user_has_permission``."""
        from .access import user_has_permission

        return user_has_permission(self, model_name, action, project_id=project_id)


# =============================================================================
# Project Task Force (§15.3)
# =============================================================================


class ProjectTaskForce(TimeStampedModel):
    """Engineering project group — one per ProjectTenant (§15.3.1).

    ``project_id`` is a plain integer (no cross-schema FK). It may be empty
    for an administrator-created group that has not been assigned yet.
    """

    class CreatorRole(models.TextChoices):
        ADMINISTRATOR = "ADMINISTRATOR", _("Administrator")
        PROJECT_MANAGER = "PROJECT_MANAGER", _("Project Manager")
        PROJECT_ENGINEER = "PROJECT_ENGINEER", _("Project Engineer")

    project_id = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("ProjectTenant id (tenants.ProjectTenant); one group per project"),
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_task_forces",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_task_forces",
    )
    created_by_role = models.CharField(
        max_length=20, choices=CreatorRole.choices, blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Project Task Force")
        verbose_name_plural = _("Project Task Forces")
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["project_id"],
                condition=Q(project_id__isnull=False),
                name="unique_task_force_per_project",
                violation_error_code="ADM_TASK_FORCE_PROJECT_TAKEN",
                violation_error_message=_(
                    "This project already has a task force (one per project)."
                ),
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def project(self):
        if not self.project_id:
            return None
        from apps.tenants.models import ProjectTenant

        return ProjectTenant.objects.filter(pk=self.project_id).first()


class TaskForceMembership(TimeStampedModel):
    """User ↔ task force (§15.3.1)."""

    task_force = models.ForeignKey(
        ProjectTaskForce, on_delete=models.CASCADE, related_name="memberships"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_force_memberships",
    )
    role_in_project = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_memberships",
        help_text=_("Overrides the user's system role inside this project"),
    )
    joined_at = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_task_force_memberships",
    )
    is_active = models.BooleanField(default=True)

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
