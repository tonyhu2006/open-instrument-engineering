"""
Tenant Models - Project-based Schema Isolation

Each Project becomes a tenant with its own PostgreSQL schema.
Shared data (users, organizations) stays in the public schema.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django_tenants.models import TenantMixin, DomainMixin

from apps.core.models import TimeStampedModel


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
        CANCELLED = "CANCELLED", _("Cancelled")
    
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
        help_text=_(
            "Hierarchy configuration. Example: "
            "{'template': 'standard', 'levels': ['site', 'plant', 'area', 'unit']}"
        ),
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
    
    def save(self, *args, **kwargs):
        # Auto-generate schema_name from project_no if not set
        if not self.schema_name:
            # Convert project_no to valid schema name (lowercase, underscores)
            schema = self.project_no.lower().replace('-', '_').replace(' ', '_')
            # Ensure it starts with a letter
            if schema[0].isdigit():
                schema = f"prj_{schema}"
            self.schema_name = schema
        super().save(*args, **kwargs)


class ProjectDomain(DomainMixin):
    """
    ProjectDomain - Maps domains/subdomains to project tenants.
    
    For API-based access, we use a header-based tenant selection,
    but domains can be used for direct project access.
    """
    
    class Meta:
        verbose_name = _("Project Domain")
        verbose_name_plural = _("Project Domains")
    
    def __str__(self):
        return self.domain
