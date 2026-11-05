from rest_framework import viewsets

from apps.administration.permissions import RoleMatrixPermission

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Audit trail — read-only, Administrator only (ADM-07, §15.2.4)."""

    queryset = AuditLog.objects.select_related("organization", "user").all()
    serializer_class = AuditLogSerializer
    permission_classes = [RoleMatrixPermission]
    rbac_resource = "audit_log"
    filterset_fields = [
        "organization",
        "project_id",
        "user",
        "action",
        "model_name",
        "object_id",
        "batch_id",
    ]
    search_fields = ["object_repr", "model_name"]
    ordering = ["-timestamp"]
