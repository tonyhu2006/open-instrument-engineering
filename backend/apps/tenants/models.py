"""
Tenant Models - Project-based Schema Isolation

Each Project becomes a tenant with its own PostgreSQL schema.
Shared data (users, organizations) stays in the public schema.
"""

import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_tenants.models import DomainMixin, TenantMixin

from apps.core.models import TimeStampedModel

from .hierarchy_config import validate as validate_hierarchy_config


class ProjectTenant(TenantMixin, TimeStampedModel):
    """
    ProjectTenant - Each project gets its own PostgreSQL schema.

    The schema_name is automatically generated from the project.
    All project-specific data (tags, loops, etc.) is stored in this schema.
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        ON_HOLD = "ON_HOLD", _("On Hold")
        COMPLETED = "COMPLETED", _("Completed")
        ARCHIVED = "ARCHIVED", _("Archived")

    # Tenant identification
    name = models.CharField(
        max_length=300,
        help_text=_("Project name"),
    )
    project_no = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Project number (e.g., 'PRJ-2024-001')"),
    )

    # Organization reference (stored in public schema)
    organization_id = models.IntegerField(
        help_text=_("Organization ID this project belongs to"),
    )

    # Project metadata
    description = models.TextField(
        blank=True,
        help_text=_("Project description"),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text=_("Project status"),
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Project start date"),
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Project end date"),
    )
    hierarchy_config = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Hierarchy configuration (§15.4.6, schema_version 1)"),
    )

    # django-tenants settings
    auto_create_schema = True
    auto_drop_schema = True

    class Meta:
        verbose_name = _("Project Tenant")
        verbose_name_plural = _("Project Tenants")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project_no} - {self.name}"

    @staticmethod
    def schema_name_for(project_no: str) -> str:
        """§15.4.1: ``project_`` + lower-case alphanumerics of the project no.

        e.g. ``PRJ-2025-001`` → ``project_prj2025001``.
        """
        core = re.sub(r"[^a-z0-9]", "", (project_no or "").lower())
        return f"project_{core}"[:63]

    def clean(self):
        super().clean()
        errors = {}
        candidate = self.schema_name or self.schema_name_for(self.project_no)
        if candidate == "project_":
            errors["project_no"] = _(
                "Project number must contain at least one letter or digit."
            )
        config_errors = validate_hierarchy_config(self.hierarchy_config)
        if config_errors:
            errors["hierarchy_config"] = config_errors
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Existing tenants keep their stored schema_name; new ones derive it.
        if not self.schema_name:
            self.schema_name = self.schema_name_for(self.project_no)
        super().save(*args, **kwargs)


class ProjectDomain(DomainMixin):
    """
    ProjectDomain - django-tenants contract model. NOT used at runtime.

    This project routes tenants via the X-Project-ID HTTP header
    (see apps.tenants.middleware.HeaderBasedTenantMiddleware), NOT via
    Host-header / subdomain matching. Therefore this model has no
    operational role: rows here are never queried during request handling.

    The class is preserved only because django-tenants requires
    settings.TENANT_DOMAIN_MODEL to point at a concrete subclass of
    DomainMixin. Removing the class would force a fork of django-tenants.

    Operationally this table SHOULD remain empty. The model is therefore
    not registered in Django admin and exposes no DRF endpoint. If the
    deployment ever migrates to subdomain-based routing, switch the
    middleware back to django_tenants.middleware.TenantMainMiddleware
    and populate this table accordingly.
    """

    class Meta:
        verbose_name = _("Project Domain")
        verbose_name_plural = _("Project Domains")

    def __str__(self):
        return self.domain
