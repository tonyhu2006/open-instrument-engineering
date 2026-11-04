"""
Audit models (public schema) — SPECIFICATION §6.1.1 / ADM-07 / §4.1.13.

AuditLog is append-only: rows can be inserted but never updated or deleted
through the ORM (``save`` on an existing row, ``delete`` and queryset
``update``/``delete`` all raise).
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditLogImmutableError(RuntimeError):
    """Raised on any attempt to modify or delete an audit record."""


class AuditLogQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise AuditLogImmutableError("Audit log records are append-only.")

    def delete(self):
        raise AuditLogImmutableError("Audit log records are append-only.")


class AuditLog(models.Model):
    """Who / When / What for every CREATE / UPDATE / DELETE (ADM-07)."""

    class Action(models.TextChoices):
        CREATE = "CREATE", _("Create")
        READ = "READ", _("Read")
        UPDATE = "UPDATE", _("Update")
        DELETE = "DELETE", _("Delete")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "administration.Organization",
        on_delete=models.SET_NULL,
        related_name="audit_logs",
        null=True,
        blank=True,
    )
    project_id = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("ProjectTenant id (no cross-schema FK)"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=10, choices=Action.choices)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=500, blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    changed_fields = models.JSONField(default=list, blank=True)
    change_details = models.JSONField(
        default=dict, blank=True, help_text=_("§6.1.2 change marker structure")
    )
    batch_id = models.UUIDField(
        null=True, blank=True, db_index=True, help_text=_("Bulk operation id")
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = AuditLogQuerySet.as_manager()

    class Meta:
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(
                fields=["organization", "-timestamp"], name="audit_audit_organiz_idx"
            ),
            models.Index(
                fields=["project_id", "-timestamp"], name="audit_audit_project_idx"
            ),
            models.Index(fields=["user", "-timestamp"], name="audit_audit_user_id_idx"),
            models.Index(
                fields=["model_name", "object_id"], name="audit_audit_model_n_idx"
            ),
        ]

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name}:{self.object_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise AuditLogImmutableError("Audit log records are append-only.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise AuditLogImmutableError("Audit log records are append-only.")

    @property
    def project(self):
        if not self.project_id:
            return None
        from apps.tenants.models import ProjectTenant

        return ProjectTenant.objects.filter(pk=self.project_id).first()
