"""
Core App Models - abstract base classes (SPECIFICATION §4.1.1 / §4.1.8).

| Abstract class      | Responsibility                                            |
|---------------------|-----------------------------------------------------------|
| TimeStampedModel    | created_at / updated_at                                   |
| AuditedModel        | + created_by / updated_by                                 |
| SoftDeleteModel     | is_deleted + SoftDeleteManager (``alive``)                |
| VersionedModel      | row_version (optimistic lock, §4.1.3)                     |
| TenantBaseModel     | Audited + SoftDelete + Versioned — tenant business tables |
| ProjectScopedModel  | project_id — public-schema cross-project models           |

Cross-schema references (AGENTS.md hard rule 2): tenant tables cannot hold a
real ForeignKey to ``administration.User`` (public schema), so ``created_by``
/ ``updated_by`` are stored as plain integer ids and exposed as properties
that perform an explicit lookup. See docs/OPEN_QUESTIONS.md OQ-003.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Abstract base model with created and modified timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def _lookup_user(user_id):
    if not user_id:
        return None
    from django.contrib.auth import get_user_model

    return get_user_model().objects.filter(pk=user_id).first()


class AuditedModel(TimeStampedModel):
    """Adds who-created / who-updated (§4.1.1)."""

    created_by_id = models.IntegerField(
        null=True, blank=True, help_text=_("User id of the creator (public schema)")
    )
    updated_by_id = models.IntegerField(
        null=True, blank=True, help_text=_("User id of the last editor")
    )

    class Meta:
        abstract = True

    @property
    def created_by(self):
        return _lookup_user(self.created_by_id)

    @property
    def updated_by(self):
        return _lookup_user(self.updated_by_id)


class SoftDeleteQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Manager that hides soft-deleted rows (§4.1.2)."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    """Soft delete flag (§4.1.2). Rows are never hard-deleted through the API.

    ``objects`` stays unfiltered (MPTT, unique validation and admin rely on
    seeing every row); use ``Model.alive`` or ``objects.alive()`` for the
    visible set.
    """

    is_deleted = models.BooleanField(
        default=False, db_index=True, help_text=_("Soft delete flag")
    )

    objects = models.Manager.from_queryset(SoftDeleteQuerySet)()
    alive = SoftDeleteManager()

    class Meta:
        abstract = True


class VersionedModel(models.Model):
    """Optimistic lock version (§4.1.3): incremented on every update."""

    row_version = models.PositiveIntegerField(
        default=1, help_text=_("Optimistic lock version")
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding and self.pk is not None:
            self.row_version = (self.row_version or 0) + 1
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = set(update_fields) | {"row_version"}
        super().save(*args, **kwargs)


class TenantBaseModel(AuditedModel, SoftDeleteModel, VersionedModel):
    """Base class for tenant-schema business tables (§4.1.8)."""

    class Meta:
        abstract = True


class ProjectScopedModel(TimeStampedModel):
    """Base class for public-schema cross-project models (§4.1.8).

    ``project_id`` is a plain integer (no cross-schema FK, AGENTS.md rule 2).
    """

    project_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("ProjectTenant id (tenants.ProjectTenant)"),
    )

    class Meta:
        abstract = True

    @property
    def project(self):
        if not self.project_id:
            return None
        from apps.tenants.models import ProjectTenant

        return ProjectTenant.objects.filter(pk=self.project_id).first()


__all__ = [
    "AuditedModel",
    "ProjectScopedModel",
    "SoftDeleteManager",
    "SoftDeleteModel",
    "SoftDeleteQuerySet",
    "TenantBaseModel",
    "TimeStampedModel",
    "VersionedModel",
]
